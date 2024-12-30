package com.thecodinginterface.gsrconsumer;

import com.amazonaws.services.schemaregistry.deserializers.GlueSchemaRegistryKafkaDeserializer;
import com.amazonaws.services.schemaregistry.utils.AWSSchemaRegistryConstants;
import com.amazonaws.services.simplesystemsmanagement.AWSSimpleSystemsManagementClientBuilder;
import com.amazonaws.services.simplesystemsmanagement.model.GetParameterRequest;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.ByteArraySerializer;
import org.apache.kafka.common.serialization.ByteArrayDeserializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.kafka.KafkaProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.config.TopicBuilder;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.ProducerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.listener.ContainerProperties;
import software.amazon.awssdk.services.glue.model.DataFormat;

import java.util.HashMap;
import java.util.Map;


@Configuration
public class KafkaConfig {
    @Value("${kafka-topics.common-settings.default-partitions}")
    int defaultPartitions;

    @Value("${kafka-topics.common-settings.default-replicas}")
    int defaultReplicas;

    @Value("${spring.application.name}")
    String appName;

    @Value("${kafka-topics.common-settings.registry-name}")
    String registryName;

    @Value("${aws.region}")
    String awsRegion;

    @Value("${kafka-topics.topics.chat-messages-copy}")
    String chatMessagesCopyTopic;

    @Bean
    public KafkaAdmin.NewTopics createTopics() {
        return new KafkaAdmin.NewTopics(
                TopicBuilder.name(chatMessagesCopyTopic)
                        .partitions(defaultPartitions)
                        .replicas(defaultReplicas)
                        .build()
        );
    }

    @Bean
    public KafkaAdmin adminClient(KafkaProperties kafkaProps) {
        var cfg = new HashMap<>(kafkaProps.buildAdminProperties());
        cfg.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers(kafkaProps));
        return new KafkaAdmin(cfg);
    }


    public String bootstrapServers(KafkaProperties kafkaProps) {
        var ssmParamName = kafkaProps.getBootstrapServers().get(0);
        var ssm = AWSSimpleSystemsManagementClientBuilder.defaultClient();
        var request = new GetParameterRequest().withName(ssmParamName);
        var response = ssm.getParameter(request);
        return response.getParameter().getValue();
    }

    public Map<String, Object> consumerConfigs(KafkaProperties kafkaProps) {
        var cfg = new HashMap<>(kafkaProps.buildConsumerProperties());
        cfg.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers(kafkaProps));
        cfg.put(ConsumerConfig.GROUP_ID_CONFIG, appName);
        cfg.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest");
        cfg.put(AWSSchemaRegistryConstants.REGISTRY_NAME, registryName);
        cfg.put(AWSSchemaRegistryConstants.SCHEMA_NAMING_GENERATION_CLASS, com.thecodinginterface.gsrconsumer.GlueSchemaNamingStrategy.class);
        cfg.put(AWSSchemaRegistryConstants.DATA_FORMAT, DataFormat.JSON.name());
        cfg.put(AWSSchemaRegistryConstants.AWS_REGION, awsRegion);
        cfg.put(AWSSchemaRegistryConstants.SCHEMA_AUTO_REGISTRATION_SETTING, true);
        return cfg;
    }

    public Map<String, Object> producerConfigs(KafkaProperties kafkaProps) {
        // This is the same as the producerConfigs method in the producer app minus the schema registry properties
        // and the GlueSchemaNamingStrategy class as it is not required for a shallow copy producer which is going
        // to simply transfer bytes in the kafka message. 
        var cfg = new HashMap<>(kafkaProps.buildProducerProperties());
        cfg.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers(kafkaProps));
        return cfg;
    }

    @Bean
    public ConsumerFactory<String, Object> consumerFactory(KafkaProperties kafkaProps) {
        return new DefaultKafkaConsumerFactory<>(
          consumerConfigs(kafkaProps),
          new StringDeserializer(),
          new GlueSchemaRegistryKafkaDeserializer()
        );
    }

    @Bean
    public ConsumerFactory<String, byte[]> rawConsumerFactory(KafkaProperties kafkaProps) {
        return new DefaultKafkaConsumerFactory<>(
          consumerConfigs(kafkaProps),
          new StringDeserializer(),
          new ByteArrayDeserializer()
        );
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, Object> listenerContainerFactory(
            KafkaProperties kafkaProps) {
        var factory = new ConcurrentKafkaListenerContainerFactory<String, Object>();
        factory.setConsumerFactory(consumerFactory(kafkaProps));
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.RECORD);
        return factory;
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, byte[]> rawListenerContainerFactory(
            KafkaProperties kafkaProps) {
        var factory = new ConcurrentKafkaListenerContainerFactory<String, byte[]>();
        factory.setConsumerFactory(rawConsumerFactory(kafkaProps));
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.RECORD);
        return factory;
    }

    @Bean
    public ProducerFactory<String, ?> producerFactory(KafkaProperties kafkaProps) {
        return new DefaultKafkaProducerFactory<>(
                producerConfigs(kafkaProps),
                new StringSerializer(),
                new ByteArraySerializer()
        );
    }

    @Bean
    public KafkaTemplate<String, ?> kafkaTemplate(KafkaProperties kafkaProps) {
        return new KafkaTemplate<>(producerFactory(kafkaProps));
    }
}
