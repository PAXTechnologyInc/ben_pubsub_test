package com.pax.test

import com.pax.market.api.sdk.java.api.base.dto.Result
import com.pax.market.api.sdk.java.api.merchant.MerchantApi
import com.pax.market.api.sdk.java.api.merchant.dto.MerchantCreateRequest
import com.pax.market.api.sdk.java.api.merchant.dto.MerchantDTO
import com.pax.market.api.sdk.java.api.merchant.dto.MerchantPageDTO
import com.pax.market.api.sdk.java.api.reseller.ResellerApi
import com.pax.market.api.sdk.java.api.reseller.dto.ResellerCreateRequest
import com.pax.market.api.sdk.java.api.reseller.dto.ResellerDTO
import com.pax.market.api.sdk.java.api.reseller.dto.ResellerPageDTO
import com.pax.market.api.sdk.java.api.terminal.TerminalApi
import com.pax.market.api.sdk.java.api.terminal.dto.TerminalCreateRequest
import com.pax.market.api.sdk.java.api.terminal.dto.TerminalDTO
import com.pax.market.api.sdk.java.api.terminal.dto.TerminalUpdateRequest
import com.pax.market.api.sdk.java.api.terminalApk.TerminalApkApi
import com.pax.market.api.sdk.java.api.terminalApk.dto.CreateTerminalApkRequest
import com.pax.market.api.sdk.java.api.terminalApk.dto.TerminalApkDTO
import com.pax.market.api.sdk.java.api.terminalRki.TerminalRkiApi
import com.pax.market.api.sdk.java.api.terminalRki.dto.PushRki2TerminalRequest
import com.pax.market.api.sdk.java.api.terminalRki.dto.PushRkiTaskDTO
import org.slf4j.LoggerFactory

/**
 * Paxstore API Client wrapper
 * 
 * Uses the official Paxstore SDK (com.whatspos.sdk:3rdsys-openapi)
 */
class PaxstoreClient(
    private val config: PaxstoreConfig
) {
    private val logger = LoggerFactory.getLogger(PaxstoreClient::class.java)
    
    // Lazy-initialized API instances
    private val terminalApi by lazy { 
        TerminalApi(config.baseUrl, config.apiKey, config.apiToken) 
    }
    
    private val merchantApi by lazy { 
        MerchantApi(config.baseUrl, config.apiKey, config.apiToken) 
    }
    
    private val resellerApi by lazy { 
        ResellerApi(config.baseUrl, config.apiKey, config.apiToken) 
    }
    
    private val terminalApkApi by lazy { 
        TerminalApkApi(config.baseUrl, config.apiKey, config.apiToken) 
    }
    
    private val terminalRkiApi by lazy { 
        TerminalRkiApi(config.baseUrl, config.apiKey, config.apiToken) 
    }

    // ========== Terminal Operations ==========
    
    /**
     * Search for a terminal by TID
     */
    fun searchTerminal(
        tid: String,
        resellerName: String? = null,
        merchantName: String? = null
    ): Result<TerminalDTO> {
        logger.info("Searching terminal: tid=$tid, resellerName=$resellerName, merchantName=$merchantName")
        return terminalApi.searchTerminal(1, 10, null, resellerName, merchantName, null, tid)
    }
    
    /**
     * Get terminal by ID
     */
    fun getTerminal(terminalId: Long): Result<TerminalDTO> {
        logger.info("Getting terminal: terminalId=$terminalId")
        return terminalApi.getTerminal(terminalId)
    }
    
    /**
     * Create a new terminal
     */
    fun createTerminal(request: TerminalCreateRequest): Result<TerminalDTO> {
        logger.info("Creating terminal: name=${request.name}, tid=${request.tid}")
        return terminalApi.createTerminal(request)
    }
    
    /**
     * Update an existing terminal
     */
    fun updateTerminal(terminalId: Long, request: TerminalUpdateRequest): Result<TerminalDTO> {
        logger.info("Updating terminal: terminalId=$terminalId")
        return terminalApi.updateTerminal(terminalId, request)
    }
    
    /**
     * Activate a terminal
     */
    fun activateTerminal(terminalId: Long): Result<String> {
        logger.info("Activating terminal: terminalId=$terminalId")
        return terminalApi.activateTerminal(terminalId)
    }
    
    /**
     * Disable a terminal
     */
    fun disableTerminal(terminalId: Long): Result<String> {
        logger.info("Disabling terminal: terminalId=$terminalId")
        return terminalApi.disableTerminal(terminalId)
    }
    
    /**
     * Delete a terminal
     */
    fun deleteTerminal(terminalId: Long): Result<String> {
        logger.info("Deleting terminal: terminalId=$terminalId")
        return terminalApi.deleteTerminal(terminalId)
    }
    
    /**
     * Lock a terminal
     */
    fun lockTerminal(terminalId: Long): Result<String> {
        logger.info("Locking terminal: terminalId=$terminalId")
        return terminalApi.pushCmdToTerminal(terminalId, TerminalApi.TerminalPushCmd.Lock)
    }
    
    /**
     * Unlock a terminal
     */
    fun unlockTerminal(terminalId: Long): Result<String> {
        logger.info("Unlocking terminal: terminalId=$terminalId")
        return terminalApi.pushCmdToTerminal(terminalId, TerminalApi.TerminalPushCmd.Unlock)
    }

    // ========== Merchant Operations ==========
    
    /**
     * Search merchants by name
     */
    fun searchMerchant(merchantName: String): Result<MerchantPageDTO> {
        logger.info("Searching merchant: name=$merchantName")
        return merchantApi.searchMerchant(1, 10, null, merchantName, null)
    }
    
    /**
     * Create a new merchant
     */
    fun createMerchant(request: MerchantCreateRequest): Result<MerchantDTO> {
        logger.info("Creating merchant: name=${request.name}")
        return merchantApi.createMerchant(request)
    }
    
    /**
     * Activate a merchant
     */
    fun activateMerchant(merchantId: Long): Result<String> {
        logger.info("Activating merchant: merchantId=$merchantId")
        return merchantApi.activateMerchant(merchantId)
    }
    
    /**
     * Disable a merchant
     */
    fun disableMerchant(merchantId: Long): Result<String> {
        logger.info("Disabling merchant: merchantId=$merchantId")
        return merchantApi.disableMerchant(merchantId)
    }

    // ========== Reseller Operations ==========
    
    /**
     * Search resellers by name
     */
    fun searchReseller(resellerName: String): Result<ResellerPageDTO> {
        logger.info("Searching reseller: name=$resellerName")
        return resellerApi.searchReseller(1, 10, null, resellerName, null)
    }
    
    /**
     * Create a new reseller
     */
    fun createReseller(request: ResellerCreateRequest): Result<ResellerDTO> {
        logger.info("Creating reseller: name=${request.name}")
        return resellerApi.createReseller(request)
    }
    
    /**
     * Activate a reseller
     */
    fun activateReseller(resellerId: Long): Result<String> {
        logger.info("Activating reseller: resellerId=$resellerId")
        return resellerApi.activateReseller(resellerId)
    }

    // ========== Terminal APK Operations ==========
    
    /**
     * Search terminal APK pushes
     */
    fun searchTerminalApk(
        tid: String,
        packageName: String,
        status: TerminalApkApi.PushStatus? = null
    ): Result<TerminalApkDTO> {
        logger.info("Searching terminal APK: tid=$tid, packageName=$packageName")
        return terminalApkApi.searchTerminalApk(
            1, 10, TerminalApkApi.SearchOrderBy.CreatedDate_desc, 
            tid, packageName, status
        )
    }
    
    /**
     * Create a terminal APK push
     */
    fun createTerminalApk(request: CreateTerminalApkRequest): Result<TerminalApkDTO> {
        logger.info("Creating terminal APK push: tid=${request.tid}")
        return terminalApkApi.createTerminalApk(request)
    }

    // ========== Terminal RKI Operations ==========
    
    /**
     * Push RKI key to terminal
     */
    fun pushRkiToTerminal(request: PushRki2TerminalRequest): Result<PushRkiTaskDTO> {
        logger.info("Pushing RKI to terminal: tid=${request.tid}")
        return terminalRkiApi.pushRkiKey2Terminal(request)
    }

    companion object {
        /**
         * Create client from config file
         */
        fun fromConfigFile(configPath: String = "paxstore_config.yml"): PaxstoreClient {
            val config = PaxstoreConfig.load(configPath)
            return PaxstoreClient(config)
        }
    }
}
