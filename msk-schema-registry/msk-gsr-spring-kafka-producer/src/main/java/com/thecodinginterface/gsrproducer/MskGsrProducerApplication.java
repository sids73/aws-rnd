package com.thecodinginterface.gsrproducer;

import com.thecodinginterface.schemas.ChatMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;

import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;

@EnableScheduling
@SpringBootApplication
public class MskGsrProducerApplication {

	static final Logger log = LoggerFactory.getLogger(MskGsrProducerApplication.class);

	KafkaConfig kafkaConfig;
	KafkaTemplate<String, ChatMessage> kafkaTemplate;
	public MskGsrProducerApplication(KafkaConfig kafkaConfig, KafkaTemplate<String, ChatMessage> kafkaTemplate) {
		this.kafkaConfig = kafkaConfig;
		this.kafkaTemplate = kafkaTemplate;
	}

	public static void main(String[] args) {
		SpringApplication.run(MskGsrProducerApplication.class, args);
	}

	static final String[] greetings = {
		"Hi",
		"Hello",
		"Howdy",
		"Hey",
		"Good morning",
		"Good afternoon",
		"Good evening",
		"How's it going?"
	};

	static final String[] names = {
			"Andy",
			"Sarah",
			"Divya",
			"Ashok",
			"Paul"
	};

	static <T> T randomItem(T[] items) {
		return items[ThreadLocalRandom.current().nextInt(items.length)];
	}

	@Scheduled(fixedRate = 30_000)
	void publishChat() {
		var message = ChatMessage.builder()
				.withId(UUID.randomUUID().toString())
				.withMessage(randomItem(greetings))
				.withFirstName(randomItem(names))
				.build();

		kafkaTemplate.send(kafkaConfig.chatMessagesTopic, message)
				.whenComplete((result, exception) -> {
					if (exception != null) {
						log.error(String.format("Failed to publish message {}", message), exception);
					} else {
						log.info("Published message '{}'", message);
					}
				});
	}
}
