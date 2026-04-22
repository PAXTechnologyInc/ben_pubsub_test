package com.pax.test

import com.pax.market.api.sdk.java.api.terminalApk.TerminalApkApi
import com.fasterxml.jackson.databind.ObjectMapper
import ch.qos.logback.classic.Level
import ch.qos.logback.classic.Logger
import org.slf4j.LoggerFactory

/**
 * Search Terminal APK and output pure JSON (for Python bridge integration)
 */
fun main(args: Array<String>) {
    // Suppress all logging to keep stdout clean for JSON
    val rootLogger = LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME) as Logger
    rootLogger.level = Level.OFF
    
    val tid = if (args.isNotEmpty()) args[0] else ""
    val packageName = if (args.size > 1) args[1] else null
    
    if (tid.isEmpty()) {
        System.err.println("Error: TID is required")
        System.exit(1)
    }
    
    try {
        val config = PaxstoreConfig.load()
        val terminalApkApi = TerminalApkApi(config.baseUrl, config.apiKey, config.apiToken)
        
        val result = terminalApkApi.searchTerminalApk(
            1,      // pageNo
            100,    // pageSize
            TerminalApkApi.SearchOrderBy.CreatedDate_desc,
            tid,
            packageName,
            null    // status
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
