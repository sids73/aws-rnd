package com.thecodinginterface.mskiamspringkafka;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;
import org.springframework.kafka.core.KafkaAdmin;


@Configuration
public class KafkaConfig {
    @Value("${kafka-topics.common-settings.default-partitions}")
    int defaultPartitions;

    @Value("${kafka-topics.common-settings.default-replicas}")
    int defaultReplicas;

    @Value("${kafka-topics.topics.english-greetings}")
    String englishGreetingsTopic;

    @Bean
    public KafkaAdmin.NewTopics createTopics() {
        return new KafkaAdmin.NewTopics(
                TopicBuilder.name(englishGreetingsTopic)
                        .partitions(defaultPartitions)
                        .replicas(defaultReplicas)
                        .build()
        );
    }
}
