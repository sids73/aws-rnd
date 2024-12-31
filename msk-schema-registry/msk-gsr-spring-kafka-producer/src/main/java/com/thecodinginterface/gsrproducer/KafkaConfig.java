package com.thecodinginterface.gsrproducer;

import com.amazonaws.services.schemaregistry.serializers.GlueSchemaRegistryKafkaSerializer;
import com.amazonaws.services.schemaregistry.utils.AWSSchemaRegistryConstants;
import com.amazonaws.services.simplesystemsmanagement.AWSSimpleSystemsManagementClientBuilder;
import com.amazonaws.services.simplesystemsmanagement.model.GetParameterRequest;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.kafka.KafkaProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Description;
import org.springframework.kafka.config.TopicBuilder;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.core.ProducerFactory;
import software.amazon.awssdk.services.glue.model.DataFormat;

import java.util.HashMap;
import java.util.Map;


@Configuration
public class KafkaConfig {
    @Value("${kafka-topics.common-settings.default-partitions}")
    int defaultPartitions;

    @Value("${kafka-topics.common-settings.default-replicas}")
    int defaultReplicas;

    @Value("${kafka-topics.topics.chat-messages}")
    String chatMessagesTopic;

    @Value("${kafka-topics.common-settings.registry-name}")
    String registryName;

    @Value("${aws.region}")
    String awsRegion;

    @Bean
    @Description("This Helps create the chat-messages topic if it does not already exist")
    public KafkaAdmin.NewTopics createTopics() {
        return new KafkaAdmin.NewTopics(
                TopicBuilder.name(chatMessagesTopic)
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

    public Map<String, Object> producerConfigs(KafkaProperties kafkaProps) {
        var cfg = new HashMap<>(kafkaProps.buildProducerProperties());
        cfg.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers(kafkaProps));
        cfg.put(AWSSchemaRegistryConstants.REGISTRY_NAME, registryName);
        cfg.put(AWSSchemaRegistryConstants.SCHEMA_NAMING_GENERATION_CLASS, com.thecodinginterface.gsrproducer.GlueSchemaNamingStrategy.class.getName());
        cfg.put(AWSSchemaRegistryConstants.DATA_FORMAT, DataFormat.JSON.name());
        cfg.put(AWSSchemaRegistryConstants.AWS_REGION, awsRegion);
        cfg.put(AWSSchemaRegistryConstants.SCHEMA_AUTO_REGISTRATION_SETTING, true);
        return cfg;
    }

    @Bean
    public ProducerFactory<String, ?> producerFactory(KafkaProperties kafkaProps) {
        return new DefaultKafkaProducerFactory<>(
                producerConfigs(kafkaProps),
                new StringSerializer(),
                new GlueSchemaRegistryKafkaSerializer()
        );
    }

    @Bean
    public KafkaTemplate<String, ?> kafkaTemplate(KafkaProperties kafkaProps) {
        return new KafkaTemplate<>(producerFactory(kafkaProps));
    }
}
