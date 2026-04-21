package com.pax.test

import com.pax.market.api.sdk.java.api.terminalApk.TerminalApkApi
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.SerializationFeature

/**
 * Test script to search Terminal APK pushes and print the full response
 */
fun main(args: Array<String>) {
    println("=" .repeat(60))
    println("Search Terminal APK Test")
    println("=" .repeat(60))
    
    // Get TID from arguments or use default (from TC-01)
    val tid = if (args.isNotEmpty()) args[0] else "000000227874"
    // PackageName - empty string to search all APKs for this terminal
    val packageName = if (args.size > 1) args[1] else ""
    
    try {
        // Load config
        println("\n[1] Loading configuration...")
        val config = PaxstoreConfig.load()
        println("    Base URL: ${config.baseUrl}")
        
        // Create TerminalApkApi directly
        println("\n[2] Creating TerminalApkApi...")
        val terminalApkApi = TerminalApkApi(config.baseUrl, config.apiKey, config.apiToken)
        
        // Search terminal APK
        println("\n[3] Searching terminal APK...")
        println("    TID: $tid")
        println("    PackageName: ${if (packageName.isEmpty()) "(all)" else packageName}")
        
        val result = terminalApkApi.searchTerminalApk(
            1,      // pageNo
            100,    // pageSize
            TerminalApkApi.SearchOrderBy.CreatedDate_desc,
            tid,
            packageName.ifEmpty { null },  // null for all packages
            null    // status - null for all statuses
        )
        
        // Print raw JSON response
        println("\n[4] Raw JSON Response:")
        println("-".repeat(60))
        val mapper = ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT)
        println(mapper.writeValueAsString(result))
        println("-".repeat(60))
        
        // Print summary
        println("\n[5] Summary:")
        println("    Business Code: ${result.businessCode}")
        println("    Message: ${result.message}")
        println("    Success: ${result.businessCode == 0}")
        
        if (result.businessCode == 0 && result.pageInfo != null) {
            println("\n    Page Info:")
            println("      Page No: ${result.pageInfo.pageNo}")
            println("      Limit: ${result.pageInfo.limit}")
            println("      Total Count: ${result.pageInfo.totalCount}")
            println("      Has Next: ${result.pageInfo.isHasNext}")
            println("      Records: ${result.pageInfo.dataSet?.size ?: 0}")
            
            // Verify totalCount == 2
            println("\n[6] Assertion:")
            val totalCount = result.pageInfo.totalCount
            if (totalCount == 2L) {
                println("    ✓ PASS: totalCount == 2")
            } else {
                println("    ✗ FAIL: Expected totalCount=2, but got totalCount=$totalCount")
            }
            
            // List APKs (dataSet contains the records)
            println("\n    APK Records (see raw JSON above for full details)")
        }
        
        println("\n    Rate Limit Info:")
        println("      Limit: ${result.rateLimit}")
        println("      Remaining: ${result.rateLimitRemain}")
        println("      Reset: ${result.rateLimitReset}")
        
    } catch (e: Exception) {
        println("\nError: ${e.message}")
        e.printStackTrace()
    }
    
    println("\n" + "=" .repeat(60))
}
