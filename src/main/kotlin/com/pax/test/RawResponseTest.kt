package com.pax.test

import com.pax.market.api.sdk.java.api.terminal.TerminalApi
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.SerializationFeature

/**
 * Test to show raw JSON response from Paxstore API
 */
fun main(args: Array<String>) {
    println("=" .repeat(60))
    println("Paxstore API - Raw JSON Response Test")
    println("=" .repeat(60))
    
    val tid = if (args.isNotEmpty()) args[0] else "000000227874"
    
    try {
        // Load config
        val config = PaxstoreConfig.load()
        println("\nBase URL: ${config.baseUrl}")
        println("API Key: ${config.apiKey}")
        
        // Create terminal API directly
        val terminalApi = TerminalApi(config.baseUrl, config.apiKey, config.apiToken)
        
        // Search terminal
        println("\n[1] Searching terminal with TID = '$tid'...")
        val searchResult = terminalApi.searchTerminal(1, 10, null, null, null, null, tid)
        
        // Convert to JSON
        val mapper = ObjectMapper().apply {
            enable(SerializationFeature.INDENT_OUTPUT)
        }
        
        println("\n[2] Raw JSON Response (Search):")
        println("-".repeat(60))
        println(mapper.writeValueAsString(searchResult))
        
        // If found, get details
        if (searchResult.businessCode == 0 && searchResult.pageInfo?.dataSet?.isNotEmpty() == true) {
            val terminalId = searchResult.pageInfo.dataSet[0].id
            
            println("\n[3] Getting terminal details for ID = $terminalId...")
            val detailResult = terminalApi.getTerminal(terminalId)
            
            println("\n[4] Raw JSON Response (Get Terminal):")
            println("-".repeat(60))
            println(mapper.writeValueAsString(detailResult))
        }
        
    } catch (e: Exception) {
        println("\nError: ${e.message}")
        e.printStackTrace()
    }
    
    println("\n" + "=" .repeat(60))
}
