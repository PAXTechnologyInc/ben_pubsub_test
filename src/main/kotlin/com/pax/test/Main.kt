package com.pax.test

import org.slf4j.LoggerFactory

/**
 * Main entry point for testing Paxstore API
 */
fun main(args: Array<String>) {
    val logger = LoggerFactory.getLogger("Main")
    
    println("=" .repeat(60))
    println("Paxstore API Test")
    println("=" .repeat(60))
    
    // Get TID from arguments or use default
    val tid = if (args.isNotEmpty()) args[0] else "000000227874"
    
    try {
        // Load config
        println("\n[1] Loading configuration...")
        val config = PaxstoreConfig.load()
        println("    Base URL: ${config.baseUrl}")
        println("    API Key: ${config.apiKey}")
        
        // Create client
        println("\n[2] Creating client...")
        val client = PaxstoreClient(config)
        println("    Client created successfully")
        
        // Search terminal
        println("\n[3] Searching terminal with TID = '$tid'...")
        val result = client.searchTerminal(tid)
        
        // If found, get full details
        var detailResult: com.pax.market.api.sdk.java.api.base.dto.Result<com.pax.market.api.sdk.java.api.terminal.dto.TerminalDTO>? = null
        if (result.businessCode == 0 && result.pageInfo?.dataSet?.isNotEmpty() == true) {
            val terminalId = result.pageInfo.dataSet[0].id
            println("\n[3.1] Getting full terminal details for ID = $terminalId...")
            detailResult = client.getTerminal(terminalId)
        }
        
        println("\n[4] Result:")
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
            
            result.pageInfo.dataSet?.forEachIndexed { index, terminal ->
                println("\n    [${ index + 1}] Terminal (Full Details):")
                println("        ===== Basic Info =====")
                println("        ID: ${terminal.id}")
                println("        Name: ${terminal.name}")
                println("        TID: ${terminal.tid}")
                println("        Serial No: ${terminal.serialNo}")
                println("        Status: ${terminal.status}")
                println("        Model: ${terminal.modelName}")
                println("        Merchant: ${terminal.merchantName}")
                println("        Reseller: ${terminal.resellerName}")
                println("        Location: ${terminal.location}")
                println("        Remark: ${terminal.remark}")
                
                println("\n        ===== Timestamps =====")
                println("        Created Date: ${terminal.createdDate}")
                println("        Updated Date: ${terminal.updatedDate}")
                println("        Last Active Time: ${terminal.lastActiveTime}")
                
                // Geo Location
                terminal.geoLocation?.let { geo ->
                    println("\n        ===== Geo Location =====")
                    println("        Latitude: ${geo.lat}")
                    println("        Longitude: ${geo.lng}")
                }
                
                // Installed Firmware
                terminal.installedFirmware?.let { fw ->
                    println("\n        ===== Installed Firmware =====")
                    println("        Firmware Name: ${fw.firmwareName}")
                    println("        Install Time: ${fw.installTime}")
                }
                
                // Installed APKs
                terminal.installedApks?.let { apks ->
                    if (apks.isNotEmpty()) {
                        println("\n        ===== Installed APKs (${apks.size}) =====")
                        apks.forEachIndexed { i, apk ->
                            println("        [APK ${i + 1}]")
                            println("          App Name: ${apk.appName}")
                            println("          Package: ${apk.packageName}")
                            println("          Version: ${apk.versionName} (${apk.versionCode})")
                            println("          Install Time: ${apk.installTime}")
                        }
                    }
                }
                
                // Terminal Detail
                terminal.terminalDetail?.let { detail ->
                    println("\n        ===== Terminal Detail =====")
                    println("        PN: ${detail.pn}")
                    println("        OS Version: ${detail.osVersion}")
                    println("        IMEI: ${detail.imei}")
                    println("        Screen Resolution: ${detail.screenResolution}")
                    println("        Language: ${detail.language}")
                    println("        IP: ${detail.ip}")
                    println("        Time Zone: ${detail.timeZone}")
                    println("        MAC Address: ${detail.macAddress}")
                    println("        ICCID: ${detail.iccid}")
                }
            }
        }
        
        println("\n    ===== Rate Limit Info =====")
        println("    Limit: ${result.rateLimit}")
        println("    Remaining: ${result.rateLimitRemain}")
        println("    Reset: ${result.rateLimitReset}")
        
        // Show detailed terminal info if available
        detailResult?.let { detail ->
            if (detail.businessCode == 0 && detail.data != null) {
                val terminal = detail.data
                println("\n" + "=" .repeat(60))
                println("[5] Full Terminal Details (from getTerminal API):")
                println("=" .repeat(60))
                
                println("\n    ===== Basic Info =====")
                println("    ID: ${terminal.id}")
                println("    Name: ${terminal.name}")
                println("    TID: ${terminal.tid}")
                println("    Serial No: ${terminal.serialNo}")
                println("    Status: ${terminal.status}")
                println("    Model: ${terminal.modelName}")
                println("    Merchant: ${terminal.merchantName}")
                println("    Reseller: ${terminal.resellerName}")
                println("    Location: ${terminal.location}")
                println("    Remark: ${terminal.remark}")
                
                println("\n    ===== Timestamps =====")
                println("    Created Date: ${terminal.createdDate}")
                println("    Updated Date: ${terminal.updatedDate}")
                println("    Last Active Time: ${terminal.lastActiveTime}")
                
                // Geo Location
                terminal.geoLocation?.let { geo ->
                    println("\n    ===== Geo Location =====")
                    println("    Latitude: ${geo.lat}")
                    println("    Longitude: ${geo.lng}")
                }
                
                // Installed Firmware
                terminal.installedFirmware?.let { fw ->
                    println("\n    ===== Installed Firmware =====")
                    println("    Firmware Name: ${fw.firmwareName}")
                    println("    Install Time: ${fw.installTime}")
                }
                
                // Installed APKs
                terminal.installedApks?.let { apks ->
                    if (apks.isNotEmpty()) {
                        println("\n    ===== Installed APKs (${apks.size}) =====")
                        apks.forEachIndexed { i, apk ->
                            println("    [APK ${i + 1}]")
                            println("      App Name: ${apk.appName}")
                            println("      Package: ${apk.packageName}")
                            println("      Version: ${apk.versionName} (${apk.versionCode})")
                            println("      Install Time: ${apk.installTime}")
                        }
                    }
                }
                
                // Terminal Detail
                terminal.terminalDetail?.let { td ->
                    println("\n    ===== Terminal Detail =====")
                    println("    PN: ${td.pn}")
                    println("    OS Version: ${td.osVersion}")
                    println("    IMEI: ${td.imei}")
                    println("    Screen Resolution: ${td.screenResolution}")
                    println("    Language: ${td.language}")
                    println("    IP: ${td.ip}")
                    println("    Time Zone: ${td.timeZone}")
                    println("    MAC Address: ${td.macAddress}")
                    println("    ICCID: ${td.iccid}")
                }
            }
        }
        
    } catch (e: Exception) {
        logger.error("Error: ${e.message}", e)
        println("\nError: ${e.message}")
    }
    
    println("\n" + "=" .repeat(60))
}
