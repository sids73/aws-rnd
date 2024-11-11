package com.thecodinginterface.mskscramspringkafka;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;

import java.util.concurrent.ThreadLocalRandom;

@EnableScheduling
@SpringBootApplication
public class MskScramSpringKafkaApplication {

	static final Logger log = LoggerFactory.getLogger(MskScramSpringKafkaApplication.class);

	KafkaSaslScramConfig kafkaConfig;
	KafkaTemplate<String, String> kafkaTemplate;
	public MskScramSpringKafkaApplication(KafkaSaslScramConfig kafkaConfig, KafkaTemplate<String, String> kafkaTemplate) {
		this.kafkaConfig = kafkaConfig;
		this.kafkaTemplate = kafkaTemplate;
	}

	public static void main(String[] args) {
		SpringApplication.run(MskScramSpringKafkaApplication.class, args);
	}

	static final String[] englishGreetings = {
			"Hi",
			"Hello",
			"Howdy",
			"Hey",
			"Good morning",
			"Good afternoon",
			"Good evening"
	};

	static final String[] multiLingualGreetings = {
			"Hello", // English
			"Bonjour", // French
			"Hola", // Spanish
			"Zdravstvute", // Russian
			"Ciao", // Italian
			"Nǐ Hǎo", // Chinese
			"Konnichiwa", // Japanese
			"Hallo", // German
			"Oi", // Portuguese
			"Anyoung", // Korean
			"Ahlan", // Arabic
			"Namaste", // Hindi
			"Shalom", // Hebrew
			"Goedendag" // Dutch
	};

	static <T> T randomItem(T[] items) {
		return items[ThreadLocalRandom.current().nextInt(items.length)];
	}

	@Scheduled(fixedRate = 30_000)
	void publishEnglishGreeting() {
		var greeting = randomItem(englishGreetings);
		kafkaTemplate.send(kafkaConfig.englishGreetingsTopic, greeting)
				.whenComplete((result, exception) -> {
					if (exception != null) {
						log.error(String.format("Failed to publish greeting {}", greeting), exception);
					} else {
						log.info("Published greeting '{}'", greeting);
					}
				});
	}

	@KafkaListener(
			topics = "${kafka-topics.topics.english-greetings}",
			groupId = "${spring.application.name}",
			containerFactory = "listenerContainerFactory")
	void handleEnglishGreeting(String greeting) {
		log.info("Consumed greeting '{}'", greeting);
	}
}
