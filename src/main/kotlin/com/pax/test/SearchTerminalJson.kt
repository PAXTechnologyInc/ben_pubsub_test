package com.pax.test

import com.pax.market.api.sdk.java.api.terminal.TerminalApi
import com.fasterxml.jackson.databind.ObjectMapper
import ch.qos.logback.classic.Level
import ch.qos.logback.classic.Logger
import org.slf4j.LoggerFactory

/**
 * Search Terminal and output pure JSON (for Python bridge integration)
 * 
 * Args:
 *   args[0] - search keyword (TID, serial number, or name)
 *   args[1] - (optional) reseller name
 *   args[2] - (optional) merchant name
 */
fun main(args: Array<String>) {
    // Suppress all logging to keep stdout clean for JSON
    val rootLogger = LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME) as Logger
    rootLogger.level = Level.OFF
    
    val searchKeyword = if (args.isNotEmpty()) args[0] else ""
    val resellerName = if (args.size > 1 && args[1].isNotEmpty()) args[1] else null
    val merchantName = if (args.size > 2 && args[2].isNotEmpty()) args[2] else null
    
    if (searchKeyword.isEmpty() && resellerName == null && merchantName == null) {
        System.err.println("Error: At least one search parameter is required")
        System.exit(1)
    }
    
    try {
        val config = PaxstoreConfig.load()
        val terminalApi = TerminalApi(config.baseUrl, config.apiKey, config.apiToken)
        
        val result = terminalApi.searchTerminal(
            1,              // pageNo
            100,            // pageSize
            null,           // orderBy
            resellerName,   // resellerName
            merchantName,   // merchantName
            null,           // status
            searchKeyword.ifEmpty { null }  // serialNo or TID
        )
        
        // Output pure JSON to stdout
        val mapper = ObjectMapper()
        println(mapper.writeValueAsString(result))
        
    } catch (e: Exception) {
        val errorJson = mapOf(
            "businessCode" to -1,
            "message" to e.message
        )
        val mapper = ObjectMapper()
        println(mapper.writeValueAsString(errorJson))
        System.exit(1)
    }
}
