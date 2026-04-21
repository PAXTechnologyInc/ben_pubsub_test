package com.pax.test

import org.yaml.snakeyaml.Yaml
import java.io.File
import java.io.FileInputStream

/**
 * Paxstore API configuration loaded from YAML file
 */
data class PaxstoreConfig(
    val baseUrl: String,
    val apiKey: String,
    val apiToken: String,
    val rkiKey: String = ""
) {
    companion object {
        /**
         * Load configuration from paxstore_config.yml
         */
        fun load(configPath: String = "paxstore_config.yml"): PaxstoreConfig {
            val yaml = Yaml()
            val configFile = File(configPath)
            
            if (!configFile.exists()) {
                throw IllegalArgumentException("Config file not found: $configPath")
            }
            
            FileInputStream(configFile).use { inputStream ->
                val config: Map<String, Any> = yaml.load(inputStream)
                
                @Suppress("UNCHECKED_CAST")
                val paxstore = config["paxstore"] as? Map<String, Any>
                    ?: throw IllegalArgumentException("Missing 'paxstore' section in config")
                
                @Suppress("UNCHECKED_CAST")
                val api = paxstore["api"] as? Map<String, Any>
                    ?: throw IllegalArgumentException("Missing 'paxstore.api' section in config")
                
                @Suppress("UNCHECKED_CAST")
                val rki = config["rki"] as? Map<String, Any> ?: emptyMap()
                
                return PaxstoreConfig(
                    baseUrl = api["base_url"]?.toString() 
                        ?: throw IllegalArgumentException("Missing 'base_url' in config"),
                    apiKey = api["key"]?.toString() 
                        ?: throw IllegalArgumentException("Missing 'key' in config"),
                    apiToken = api["token"]?.toString() 
                        ?: throw IllegalArgumentException("Missing 'token' in config"),
                    rkiKey = rki["key"]?.toString() ?: ""
                )
            }
        }
    }
}
