package com.example.terminal

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import com.example.api.CloudOpsBackendClient
import java.util.UUID

class CloudShellViewModel : ViewModel() {

    private val sessionId = UUID.randomUUID().toString()

    val terminalModel = TerminalModel(rows = 35, cols = 100)
    
    var connectionStatus by mutableStateOf("Disconnected")
        private set

    var currentWsUrl by mutableStateOf("")
        private set

    private var socket: CloudShellSocket? = null

    init {
        // Construct standard WebSocket URL dynamically from current backend URL
        val backendUrl = try {
            CloudOpsBackendClient.baseUrl
        } catch (e: Exception) {
            "http://154.205.123.215:8000"
        }

        val wsScheme = if (backendUrl.startsWith("https://")) "wss://" else "ws://"
        val cleanUrl = backendUrl.removePrefix("https://").removePrefix("http://")
        
        val wsBase = "${wsScheme}${cleanUrl}"
        val baseWs = if (wsBase.endsWith("/")) "${wsBase}ws/cloudshell" else "$wsBase/ws/cloudshell"
        currentWsUrl = "$baseWs/$sessionId"
    }

    fun connect(customUrl: String? = null) {
        val targetUrl = customUrl ?: currentWsUrl
        if (customUrl != null) {
            currentWsUrl = customUrl
        }
        
        socket?.disconnect()
        terminalModel.clearScreen()
        terminalModel.writeData("[System] Initiating link with: $targetUrl\n")

        socket = CloudShellSocket(
            onMessage = { message ->
                terminalModel.writeData(message)
            },
            onStatusChange = { status ->
                connectionStatus = status
                terminalModel.writeData("\n[System] Link $status\n")
            }
        )

        socket?.connect(targetUrl)
    }

    fun execute(command: String) {
        socket?.send(command)
    }

    fun clearTerminal() {
        terminalModel.clearScreen()
        terminalModel.writeData("[System] Terminal state reset.\n")
    }

    override fun onCleared() {
        socket?.disconnect()
    }
}
