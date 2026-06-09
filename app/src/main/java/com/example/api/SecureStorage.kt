package com.example.api

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import android.util.Log
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/**
 * Enterprise-grade SecureStorage for storing JWT Bearer access tokens and session claims.
 * Employs hardware-backed Android KeyStore AES-GCM-NoPadding hardware cryptography.
 * Falls back transparently to obfuscated storage if hardware elements are unsupported in emulation.
 */
object SecureStorage {
    private const val TAG = "SecureStorage"
    private const val PREFS_NAME = "com.cloudops.secure.vault"
    private const val KEY_ALIAS = "CloudOpsSecretStorageKey"
    private const val ANDROID_KEYSTORE = "AndroidKeyStore"
    private const val AES_MODE = "AES/GCM/NoPadding"

    // Storage Keys
    private const val KEY_TOKEN = "enc_jwt_token"
    private const val KEY_USER_EMAIL = "enc_user_email"
    private const val KEY_ORG_NAME = "enc_org_name"
    private const val KEY_ORG_ID = "enc_org_id"
    private const val KEY_ORG_PLAN = "enc_org_plan"
    private const val KEY_USER_ROLE = "enc_user_role"

    data class SessionData(
        val accessToken: String,
        val email: String,
        val orgName: String,
        val orgId: Int,
        val plan: String,
        val role: String
    )

    @Synchronized
    private fun getOrCreateSecretKey(): SecretKey? {
        return try {
            val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
            if (keyStore.containsAlias(KEY_ALIAS)) {
                val entry = keyStore.getEntry(KEY_ALIAS, null) as? KeyStore.SecretKeyEntry
                return entry?.secretKey
            }

            // Create a hardware-backed Secret Key
            val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE)
            val spec = KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setRandomizedEncryptionRequired(true)
                .build()

            keyGenerator.init(spec)
            keyGenerator.generateKey()
        } catch (e: Exception) {
            Log.e(TAG, "Hardware KeyStore failed, falling back to software emulation: ${e.message}")
            null
        }
    }

    private fun encrypt(plainText: String): String {
        if (plainText.isEmpty()) return ""
        return try {
            val secretKey = getOrCreateSecretKey()
            if (secretKey != null) {
                val cipher = Cipher.getInstance(AES_MODE)
                cipher.init(Cipher.ENCRYPT_MODE, secretKey)
                val iv = cipher.iv
                val encryptedBytes = cipher.doFinal(plainText.toByteArray(Charsets.UTF_8))
                
                // Format: IV_BASE64:CIPHERTEXT_BASE64
                val ivStr = Base64.encodeToString(iv, Base64.DEFAULT).trim()
                val cipherStr = Base64.encodeToString(encryptedBytes, Base64.DEFAULT).trim()
                "$ivStr:$cipherStr"
            } else {
                // Obfuscated software fallback if KeyStore fails
                softwareObfuscate(plainText)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Encryption routine exception: ${e.message}")
            softwareObfuscate(plainText)
        }
    }

    private fun decrypt(encryptedData: String?): String? {
        if (encryptedData.isNullOrEmpty()) return null
        return try {
            if (!encryptedData.contains(":")) {
                return softwareDeobfuscate(encryptedData)
            }
            val parts = encryptedData.split(":")
            val ivBytes = Base64.decode(parts[0], Base64.DEFAULT)
            val cipherBytes = Base64.decode(parts[1], Base64.DEFAULT)

            val secretKey = getOrCreateSecretKey()
            if (secretKey != null) {
                val cipher = Cipher.getInstance(AES_MODE)
                val spec = GCMParameterSpec(128, ivBytes)
                cipher.init(Cipher.DECRYPT_MODE, secretKey, spec)
                val decryptedBytes = cipher.doFinal(cipherBytes)
                String(decryptedBytes, Charsets.UTF_8)
            } else {
                softwareDeobfuscate(encryptedData)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Decryption routine failure, trying deobfuscated fallback: ${e.message}")
            softwareDeobfuscate(encryptedData)
        }
    }

    // obfuscation helpers (double base64 + XOR with Salt)
    private fun softwareObfuscate(plainText: String): String {
        return try {
            val xorBytes = plainText.toByteArray(Charsets.UTF_8)
            val salt = "CloudOpsSREObfuscationSaltKey1129".toByteArray()
            for (i in xorBytes.indices) {
                xorBytes[i] = (xorBytes[i].toInt() xor salt[i % salt.size].toInt()).toByte()
            }
            Base64.encodeToString(xorBytes, Base64.NO_WRAP)
        } catch (e: Exception) {
            Base64.encodeToString(plainText.toByteArray(Charsets.UTF_8), Base64.NO_WRAP)
        }
    }

    private fun softwareDeobfuscate(cipherText: String): String? {
        return try {
            val decoded = Base64.decode(cipherText, Base64.NO_WRAP)
            val salt = "CloudOpsSREObfuscationSaltKey1129".toByteArray()
            for (i in decoded.indices) {
                decoded[i] = (decoded[i].toInt() xor salt[i % salt.size].toInt()).toByte()
            }
            String(decoded, Charsets.UTF_8)
        } catch (e: Exception) {
            try {
                String(Base64.decode(cipherText, Base64.NO_WRAP), Charsets.UTF_8)
            } catch (ex: Exception) {
                null
            }
        }
    }

    fun saveToken(context: Context, token: String) {
        val sharedPrefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        sharedPrefs.edit().putString(KEY_TOKEN, encrypt(token)).apply()
        // Synchronized state with global api clients
        TokenStorage.jwtToken = token
    }

    fun getToken(context: Context): String? {
        val sharedPrefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val plain = decrypt(sharedPrefs.getString(KEY_TOKEN, null))
        if (!plain.isNullOrEmpty()) {
            TokenStorage.jwtToken = plain
        }
        return plain
    }

    fun saveSession(
        context: Context,
        token: String,
        email: String,
        orgName: String,
        orgId: Int,
        plan: String,
        role: String
    ) {
        val sharedPrefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        sharedPrefs.edit().apply {
            putString(KEY_TOKEN, encrypt(token))
            putString(KEY_USER_EMAIL, encrypt(email))
            putString(KEY_ORG_NAME, encrypt(orgName))
            putInt(KEY_ORG_ID, orgId) // OrgId int doesn't strictly need crypto, or we can store its string encrypted
            putString(KEY_ORG_PLAN, encrypt(plan))
            putString(KEY_USER_ROLE, encrypt(role))
        }.apply()
        TokenStorage.jwtToken = token
    }

    fun restoreSession(context: Context): SessionData? {
        val sharedPrefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val token = decrypt(sharedPrefs.getString(KEY_TOKEN, null)) ?: return null
        val email = decrypt(sharedPrefs.getString(KEY_USER_EMAIL, null)) ?: return null
        val orgName = decrypt(sharedPrefs.getString(KEY_ORG_NAME, null)) ?: return null
        val orgId = sharedPrefs.getInt(KEY_ORG_ID, 0)
        val plan = decrypt(sharedPrefs.getString(KEY_ORG_PLAN, null)) ?: "BASIC"
        val role = decrypt(sharedPrefs.getString(KEY_USER_ROLE, null)) ?: "ORG_ADMIN"

        TokenStorage.jwtToken = token
        return SessionData(token, email, orgName, orgId, plan, role)
    }

    fun clearSession(context: Context) {
        val sharedPrefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        sharedPrefs.edit().clear().apply()
        TokenStorage.jwtToken = null
    }
}
