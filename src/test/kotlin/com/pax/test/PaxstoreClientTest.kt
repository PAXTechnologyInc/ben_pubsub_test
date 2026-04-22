package com.pax.test

import com.pax.market.api.sdk.java.api.terminal.dto.TerminalCreateRequest
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.*
import org.junit.jupiter.api.condition.EnabledIf

/**
 * Tests for PaxstoreClient
 * 
 * Integration tests require valid API credentials in paxstore_config.yml
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class PaxstoreClientTest {
    
    private lateinit var client: PaxstoreClient
    private var configLoaded = false
    
    @BeforeAll
    fun setup() {
        try {
            client = PaxstoreClient.fromConfigFile()
            configLoaded = true
            println("Config loaded successfully")
        } catch (e: Exception) {
            println("Warning: Could not load config - ${e.message}")
            println("Integration tests will be skipped")
        }
    }
    
    private fun isConfigLoaded() = configLoaded
    
    // ========== Unit Tests (no API required) ==========
    
    @Test
    fun `config loads from yaml file`() {
        val config = PaxstoreConfig.load()
        
        assertThat(config.baseUrl).isNotBlank()
        assertThat(config.apiKey).isNotBlank()
        assertThat(config.apiToken).isNotBlank()
    }
    
    @Test
    fun `terminal create request can be built`() {
        val request = TerminalCreateRequest().apply {
            name = "Test Terminal"
            tid = "WP12345678"
            resellerName = "Test Reseller"
            merchantName = "Test Merchant"
            modelName = "A920"
        }
        
        assertThat(request.name).isEqualTo("Test Terminal")
        assertThat(request.tid).isEqualTo("WP12345678")
    }
    
    // ========== Integration Tests (require valid API credentials) ==========
    
    @Test
    @EnabledIf("isConfigLoaded")
    @DisplayName("Search terminal by TID - Integration Test")
    fun `search terminal by tid`() {
        // Skip if config not loaded
        if (!configLoaded) return
        
        val tid = "000000227874"
        val result = client.searchTerminal(tid)
        
        println("Search Terminal Result:")
        println("  Business Code: ${result.businessCode}")
        println("  Message: ${result.message}")
        
        // We expect either success (0) or a valid business error code
        assertThat(result.businessCode).isNotNull()
        
        if (result.businessCode == 0) {
            assertThat(result.pageInfo).isNotNull()
            println("  Total Count: ${result.pageInfo?.totalCount}")
        }
    }
    
    @Test
    @EnabledIf("isConfigLoaded")
    @DisplayName("Search merchant - Integration Test")
    fun `search merchant`() {
        if (!configLoaded) return
        
        val result = client.searchMerchant("Test")
        
        println("Search Merchant Result:")
        println("  Business Code: ${result.businessCode}")
        println("  Message: ${result.message}")
        
        assertThat(result.businessCode).isNotNull()
    }
    
    @Test
    @EnabledIf("isConfigLoaded")
    @DisplayName("Search reseller - Integration Test")
    fun `search reseller`() {
        if (!configLoaded) return
        
        val result = client.searchReseller("Vantiv")
        
        println("Search Reseller Result:")
        println("  Business Code: ${result.businessCode}")
        println("  Message: ${result.message}")
        
        assertThat(result.businessCode).isNotNull()
    }
    
    // ========== Error Handling Tests ==========
    
    @Test
    @EnabledIf("isConfigLoaded")
    @DisplayName("Handle invalid terminal ID gracefully")
    fun `handle invalid terminal id`() {
        if (!configLoaded) return
        
        val result = client.getTerminal(-1)
        
        // Should return an error, not throw exception
        assertThat(result.businessCode).isNotEqualTo(0)
    }
}
