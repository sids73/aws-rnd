package com.thecodinginterface.mskscramspringkafka;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.common.config.SaslConfigs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.kafka.KafkaProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.config.TopicBuilder;
import org.springframework.kafka.core.*;
import org.springframework.kafka.listener.ContainerProperties;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;
import software.amazon.awssdk.services.secretsmanager.model.GetSecretValueRequest;

import java.util.HashMap;
import java.util.Map;

@Configuration
public class KafkaSaslScramConfig {
    static final Logger log = LoggerFactory.getLogger(KafkaSaslScramConfig.class);

    @Value("${kafka-topics.common-settings.default-partitions}")
    int defaultPartitions;

    @Value("${kafka-topics.common-settings.default-replicas}")
    int defaultReplicas;

    @Value("${kafka-topics.topics.english-greetings}")
    String englishGreetingsTopic;

    @Value("${kafka-topics.topics.multilingual-greetings}")
    String multilingualGreetingsTopic;

    @Bean
    public KafkaAdmin.NewTopics createTopics() {
        return new KafkaAdmin.NewTopics(
                TopicBuilder.name(englishGreetingsTopic)
                        .partitions(defaultPartitions)
                        .replicas(defaultReplicas)
                        .build()
//                ,
//                TopicBuilder.name(multilingualGreetingsTopic)
//                        .partitions(defaultPartitions)
//                        .replicas(defaultReplicas)
//                        .build()
        );
    }

    public SecretsManagerClient createSecretsManagerClient(String region) {
        return SecretsManagerClient.builder()
                .region(Region.of(region))
                .build();
    }

    static class SaslScramCreds {
        String username;
        String password;

        public void setUsername(String username) {
            this.username = username;
        }

        public void setPassword(String password) {
            this.password = password;
        }
    }

    public Map<String, Object> commonAuthConfigs(String awsRegion, String awsSecretId) {
        var secretsMgrClient = createSecretsManagerClient(awsRegion);
        var request = GetSecretValueRequest.builder()
                .secretId(awsSecretId)
                .build();
        var response = secretsMgrClient.getSecretValue(request);

        SaslScramCreds creds = null;
        try {
            creds = new ObjectMapper().readValue(response.secretString(), SaslScramCreds.class);
        } catch (JsonProcessingException e) {
            log.error("Failed fetching aws secret", e);
            throw new RuntimeException(e.getMessage());
        }

        var cfg = new HashMap<String, Object>();
        cfg.put(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, "SASL_SSL");
        cfg.put(SaslConfigs.SASL_MECHANISM, "SCRAM-SHA-512");
        cfg.put(SaslConfigs.SASL_JAAS_CONFIG, String.format(
                "org.apache.kafka.common.security.scram.ScramLoginModule required username=\"%s\" password=\"%s\";",
                creds.username,
                creds.password
        ));
        return cfg;
    }

    @Bean
    public KafkaAdmin kafkaAdmin(KafkaProperties kafkaProps,
             @Value("${aws.region}") String awsRegion,
             @Value("${kafka-topics.common-settings.sasl-scram-secret-id}") String awsSecretId) {

        var cfg = kafkaProps.buildAdminProperties();
        cfg.putAll(commonAuthConfigs(awsRegion, awsSecretId));
        return new KafkaAdmin(cfg);
    }

    @Bean
    public ProducerFactory<?, ?> producerFactory(
            KafkaProperties kafkaProps,
            @Value("${aws.region}") String awsRegion,
            @Value("${kafka-topics.common-settings.sasl-scram-secret-id}") String awsSecretId) {

        var cfg = kafkaProps.buildProducerProperties();
        cfg.putAll(commonAuthConfigs(awsRegion, awsSecretId));
        return new DefaultKafkaProducerFactory<>(cfg);
    }

    @Bean
    public ConsumerFactory<?, ?> consumerFactory(
            KafkaProperties kafkaProps,
            @Value("${aws.region}") String awsRegion,
            @Value("${kafka-topics.common-settings.sasl-scram-secret-id}") String awsSecretId) {

        var cfg = kafkaProps.buildConsumerProperties();
        cfg.putAll(commonAuthConfigs(awsRegion, awsSecretId));
        return new DefaultKafkaConsumerFactory<>(cfg);
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> listenerContainerFactory(
            ConsumerFactory<String, String> consumerFactory) {

        var factory = new ConcurrentKafkaListenerContainerFactory<String, String>();
        factory.setConsumerFactory(consumerFactory);
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.RECORD);
        return factory;
    }
}
