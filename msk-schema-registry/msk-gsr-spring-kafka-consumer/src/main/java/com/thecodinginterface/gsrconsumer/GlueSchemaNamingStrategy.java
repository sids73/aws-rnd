package com.thecodinginterface.gsrconsumer;

import com.amazonaws.services.schemaregistry.common.AWSSchemaNamingStrategy;

public class GlueSchemaNamingStrategy implements AWSSchemaNamingStrategy {
    @Override
    public String getSchemaName(String transportName, Object data) {
        return getSchemaName(transportName);
    }

    @Override
    public String getSchemaName(String transportName, Object data, boolean isKey) {
        return getSchemaName(transportName) + (isKey ? "-key" : "-value");
    }

    @Override
    public String getSchemaName(String s) {
        return s.toLowerCase();
    }
}

