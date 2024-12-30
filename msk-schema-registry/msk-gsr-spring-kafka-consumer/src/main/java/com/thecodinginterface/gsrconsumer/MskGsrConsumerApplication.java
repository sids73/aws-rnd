package com.thecodinginterface.gsrconsumer;

import com.amazonaws.services.schemaregistry.serializers.json.JsonDataWithSchema;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.thecodinginterface.schemas.ChatMessage;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.scheduling.annotation.EnableScheduling;

@EnableScheduling
@SpringBootApplication
public class MskGsrConsumerApplication {

	static final Logger log = LoggerFactory.getLogger(MskGsrConsumerApplication.class);

	KafkaConfig kafkaConfig;
	KafkaTemplate<String, byte[]> kafkaTemplate;

	public MskGsrConsumerApplication(KafkaConfig kafkaConfig, KafkaTemplate<String, byte[]> kafkaTemplate) {
		this.kafkaConfig = kafkaConfig;
		this.kafkaTemplate = kafkaTemplate;
	}

	public static void main(String[] args) {
		SpringApplication.run(MskGsrConsumerApplication.class, args);
	}

	@KafkaListener(topics = "${kafka-topics.topics.chat-messages-copy}",
			groupId = "${spring.application.name}", containerFactory = "listenerContainerFactory")
	void handleMessage(ConsumerRecord<String, JsonDataWithSchema> record) {
		JsonDataWithSchema json = record.value();
		try {
			var chatMsg = new ObjectMapper().readValue(json.getPayload(), ChatMessage.class);
			log.info("Consumed copied original message '{}'", chatMsg);
		} catch (JsonProcessingException e) {
			log.error("Failed consuming message", e);
			throw new RuntimeException(e.getMessage());
		}
		
	}


	@KafkaListener(topics = "${kafka-topics.topics.chat-messages}",
			groupId = "${spring.application.name}", containerFactory = "rawListenerContainerFactory")
	void copyMessage(ConsumerRecord<String, byte[]> record) {
		byte[] rawData = record.value();
		kafkaTemplate.send(kafkaConfig.chatMessagesCopyTopic, rawData)
				.whenComplete((result, exception) -> {
					if (exception != null) {
						log.error(String.format("Failed to copy message {}", rawData), exception);
					} else {
						log.info("Copied message '{}'", rawData);
					}
				});
	}
}
