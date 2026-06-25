package com.example.terminal

import android.util.Log
import okhttp3.*

class CloudShellSocket(
    private val onMessage: (String) -> Unit,
    private val onStatusChange: (String) -> Unit = {}
) {
    private val client = OkHttpClient()
    private var socket: WebSocket? = null

    fun connect(serverUrl: String) {
        Log.i("CloudShellSocket", "Connecting to WebSocket URL: $serverUrl")
        onStatusChange("Connecting...")
        
        val request = Request.Builder()
            .url(serverUrl)
            .build()

        socket = client.newWebSocket(
            request,
            object : WebSocketListener() {
                override fun onOpen(webSocket: WebSocket, response: Response) {
                    Log.i("CloudShellSocket", "WebSocket successfully opened")
                    onStatusChange("Connected")
                }

                override fun onMessage(webSocket: WebSocket, text: String) {
                    onMessage(text)
                }

                override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                    Log.i("CloudShellSocket", "WebSocket closing: $code / $reason")
                    onStatusChange("Disconnecting...")
                }

                override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                    Log.i("CloudShellSocket", "WebSocket closed: $code / $reason")
                    onStatusChange("Disconnected")
                }

                override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                    Log.e("CloudShellSocket", "WebSocket failure", t)
                    onStatusChange("Error: ${t.localizedMessage ?: "Connection failed"}")
                }
            }
        )
    }

    fun send(command: String) {
        socket?.send(command)
    }

    fun disconnect() {
        socket?.close(1000, "closed")
    }
}
