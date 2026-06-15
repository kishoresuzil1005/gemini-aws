package com.example.ui.screens

import android.widget.Toast
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.CloudViewModel
import com.example.ui.theme.*

enum class AuthTab { SIGN_IN, SIGN_UP }
enum class AuthStage { MAIN, MFA, FORGOT_PASSWORD }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(
    viewModel: CloudViewModel,
    onLoginSuccess: () -> Unit
) {
    val context = LocalContext.current
    val keyboardController = LocalSoftwareKeyboardController.current

    var selectedTab by remember { mutableStateOf(AuthTab.SIGN_IN) }
    var currentStage by remember { mutableStateOf(AuthStage.MAIN) }

    // Form inputs
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    var orgName by remember { mutableStateOf("") }
    var selectedPlan by remember { mutableStateOf("PREMIUM") }
    var selectedRole by remember { mutableStateOf("ORG_ADMIN") }

    // MFA specific states
    var mfaMethod by remember { mutableStateOf("EMAIL_OTP") } // EMAIL_OTP, MICROSOFT_AUTH, GOOGLE_AUTH
    var mfaCode by remember { mutableStateOf("") }
    var mfaStep by remember { mutableStateOf(1) } // 1: Select Method, 2: Enter Code

    // Forgot Password states
    var forgotEmail by remember { mutableStateOf("") }
    var forgotCode by remember { mutableStateOf("") }
    var forgotNewPassword by remember { mutableStateOf("") }
    var forgotStep by remember { mutableStateOf(1) } // 1: Email, 2: Code & Reset

    // Loading & Error notifications
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // SRE Terminal logs to match visual identity
    val scrollState = rememberScrollState()

    // Smooth background gradient transition
    val gradientColors = listOf(
        Color(0xFF0D0C10),
        Color(0xFF13111A),
        Color(0xFF140E20)
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Brush.verticalGradient(gradientColors))
            .padding(20.dp)
            .verticalScroll(scrollState),
        contentAlignment = Alignment.Center
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .widthIn(max = 500.dp)
                .testTag("auth_panel")
                .border(1.dp, Color(0xFF2E2644), RoundedCornerShape(24.dp)),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF181524).copy(alpha = 0.95f)),
            shape = RoundedCornerShape(24.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 12.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(28.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Enterprise Header Brand
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(bottom = 12.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(42.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(Brush.horizontalGradient(listOf(CyberCyan, BentoPurplePrimary))),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.CloudSync,
                            contentDescription = "CloudOps Icon",
                            tint = Color.White,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "CLOUDOPS",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Black,
                        fontFamily = FontFamily.Monospace,
                        color = Color.White,
                        letterSpacing = 2.sp
                    )
                }

                Text(
                    text = "Multi-Cloud SRE Control Plane",
                    fontSize = 12.sp,
                    color = CyberCyan,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 24.dp)
                )

                // Error Display Banner via custom slide animated transition
                AnimatedVisibility(
                    visible = errorMessage != null,
                    enter = fadeIn() + slideInVertically(),
                    exit = fadeOut() + slideOutVertically()
                ) {
                    errorMessage?.let { error_text ->
                        Card(
                            colors = CardDefaults.cardColors(containerColor = Color(0xFFFF2B55).copy(alpha = 0.15f)),
                            border = BorderStroke(1.dp, Color(0xFFFF2B55)),
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(bottom = 16.dp),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Error,
                                        contentDescription = "Error message",
                                        tint = Color(0xFFFF2B55)
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = error_text,
                                        fontSize = 12.sp,
                                        color = Color.White,
                                        fontWeight = FontWeight.SemiBold,
                                        modifier = Modifier.weight(1f)
                                    )
                                }
                            }
                        }
                    }
                }

                // Crossfade switcher between Main Form, MFA, and Forgot Password
                AnimatedContent(
                    targetState = currentStage,
                    transitionSpec = {
                        slideInHorizontally { width -> width } + fadeIn() togetherWith
                                slideOutHorizontally { width -> -width } + fadeOut()
                    },
                    label = "auth_step_transition"
                ) { stage ->
                    when (stage) {
                        AuthStage.MAIN -> {
                            Column(modifier = Modifier.fillMaxWidth()) {
                                // Connection Engine Segmented Selector (Removed: Live API Engine only)

                                // EC2 GATEWAY INTERCONNECT CONFIGURATION
                                Card(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(bottom = 24.dp)
                                        .border(2.dp, CyberCyan, RoundedCornerShape(16.dp)),
                                    colors = CardDefaults.cardColors(containerColor = Color(0xFF0F0E13)),
                                    shape = RoundedCornerShape(16.dp)
                                ) {
                                    Column(modifier = Modifier.padding(16.dp)) {
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween,
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                Icon(
                                                    imageVector = Icons.Default.SettingsEthernet,
                                                    contentDescription = "Gateway",
                                                    tint = CyberCyan,
                                                    modifier = Modifier.size(18.dp)
                                                )
                                                Spacer(modifier = Modifier.width(8.dp))
                                                Text(
                                                    text = "GATEWAY CONFIGURATION",
                                                    fontWeight = FontWeight.Black,
                                                    fontSize = 11.sp,
                                                    color = CyberCyan,
                                                    fontFamily = FontFamily.Monospace
                                                )
                                            }
                                            
                                            val useBackend by viewModel.useBackend.collectAsState()
                                            Box(
                                                modifier = Modifier
                                                    .clip(RoundedCornerShape(6.dp))
                                                    .background(if (useBackend) Color(0xFF064E3B) else Color(0xFF7F1D1D))
                                                    .padding(horizontal = 8.dp, vertical = 2.dp)
                                            ) {
                                                Text(
                                                    text = if (useBackend) "BACKEND CONNECTED" else "OFFLINE MODE",
                                                    color = if (useBackend) Color(0xFF34D399) else Color(0xFFFCA5A5),
                                                    fontSize = 9.sp,
                                                    fontWeight = FontWeight.Bold
                                                )
                                            }
                                        }
                                        
                                        Spacer(modifier = Modifier.height(12.dp))
                                        
                                        var editingUrl by remember { mutableStateOf(com.example.api.CloudOpsBackendClient.baseUrl) }
                                        var isEditing by remember { mutableStateOf(false) }
                                        
                                        if (isEditing) {
                                            Row(
                                                verticalAlignment = Alignment.CenterVertically,
                                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                                modifier = Modifier.fillMaxWidth()
                                            ) {
                                                OutlinedTextField(
                                                    value = editingUrl,
                                                    onValueChange = { editingUrl = it },
                                                    textStyle = androidx.compose.ui.text.TextStyle(
                                                        color = Color.White,
                                                        fontSize = 14.sp
                                                    ),
                                                    colors = OutlinedTextFieldDefaults.colors(
                                                        focusedBorderColor = CyberCyan,
                                                        unfocusedBorderColor = Color(0xFF332D44)
                                                    ),
                                                    modifier = Modifier
                                                        .weight(1f)
                                                        .height(50.dp),
                                                    singleLine = true
                                                )
                                                Button(
                                                    onClick = {
                                                        viewModel.updateBackendUrl(editingUrl)
                                                        isEditing = false
                                                        Toast.makeText(context, "Gateway updated: $editingUrl", Toast.LENGTH_SHORT).show()
                                                    },
                                                    colors = ButtonDefaults.buttonColors(containerColor = CyberCyan),
                                                    contentPadding = PaddingValues(horizontal = 12.dp),
                                                    modifier = Modifier.height(44.dp)
                                                ) {
                                                    Text("Save", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = Color(0xFF0D0C10))
                                                }
                                            }
                                        } else {
                                            Row(
                                                modifier = Modifier.fillMaxWidth(),
                                                horizontalArrangement = Arrangement.SpaceBetween,
                                                verticalAlignment = Alignment.CenterVertically
                                            ) {
                                                Text(
                                                    text = com.example.api.CloudOpsBackendClient.baseUrl,
                                                    color = Color.White,
                                                    fontSize = 14.sp,
                                                    fontWeight = FontWeight.Bold,
                                                    modifier = Modifier.weight(1f)
                                                )
                                                
                                                Button(
                                                    onClick = { isEditing = true },
                                                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2C2A35)),
                                                    contentPadding = PaddingValues(horizontal = 12.dp),
                                                    modifier = Modifier.height(34.dp)
                                                ) {
                                                    Text("Edit Gateway", color = CyberCyan, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                                                }
                                            }
                                        }
                                    }
                                }

                                // Form Tab Buttons
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(bottom = 24.dp)
                                        .clip(RoundedCornerShape(12.dp))
                                        .background(Color(0xFF0B0912)),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    AuthTab.values().forEach { tab ->
                                        val active = selectedTab == tab
                                        Box(
                                            modifier = Modifier
                                                .weight(1f)
                                                .clip(RoundedCornerShape(12.dp))
                                                .background(if (active) Color(0xFF241E34) else Color.Transparent)
                                                .clickable {
                                                    selectedTab = tab
                                                    errorMessage = null
                                                }
                                                .padding(vertical = 12.dp)
                                                .testTag("tab_${tab.name.lowercase()}"),
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Text(
                                                text = if (tab == AuthTab.SIGN_IN) "Sign In" else "Create Account",
                                                color = if (active) Color.White else Color(0xFF9E9BA8),
                                                fontWeight = if (active) FontWeight.Bold else FontWeight.Medium,
                                                fontSize = 14.sp
                                            )
                                        }
                                    }
                                }

                                // Interactive Inputs
                                OutlinedTextField(
                                    value = email,
                                    onValueChange = { email = it },
                                    label = { Text("Email Directory") },
                                    leadingIcon = { Icon(Icons.Default.Email, contentDescription = "EmailIcon") },
                                    colors = OutlinedTextFieldDefaults.colors(
                                        focusedBorderColor = CyberCyan,
                                        unfocusedBorderColor = Color(0xFF332D44),
                                        focusedTextColor = Color.White,
                                        unfocusedTextColor = Color.White,
                                        focusedLabelColor = CyberCyan,
                                        unfocusedLabelColor = Color(0xFF9E9BA8)
                                    ),
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(bottom = 14.dp)
                                        .testTag("auth_email_input"),
                                    singleLine = true,
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email, imeAction = ImeAction.Next)
                                )

                                OutlinedTextField(
                                    value = password,
                                    onValueChange = { password = it },
                                    label = { Text("Encrypted Password") },
                                    leadingIcon = { Icon(Icons.Default.Lock, contentDescription = "PasswordIcon") },
                                    trailingIcon = {
                                        IconButton(onClick = { passwordVisible = !passwordVisible }) {
                                            Icon(
                                                imageVector = if (passwordVisible) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                                                contentDescription = "Toggle Visibility"
                                            )
                                        }
                                    },
                                    visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                                    colors = OutlinedTextFieldDefaults.colors(
                                        focusedBorderColor = CyberCyan,
                                        unfocusedBorderColor = Color(0xFF332D44),
                                        focusedTextColor = Color.White,
                                        unfocusedTextColor = Color.White,
                                        focusedLabelColor = CyberCyan,
                                        unfocusedLabelColor = Color(0xFF9E9BA8)
                                    ),
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(bottom = 14.dp)
                                        .testTag("auth_password_input"),
                                    singleLine = true,
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, imeAction = if (selectedTab == AuthTab.SIGN_UP) ImeAction.Next else ImeAction.Done),
                                    keyboardActions = KeyboardActions(onDone = { keyboardController?.hide() })
                                )

                                // Conditional Registration Fields
                                if (selectedTab == AuthTab.SIGN_UP) {
                                    OutlinedTextField(
                                        value = orgName,
                                        onValueChange = { orgName = it },
                                        label = { Text("Organization Name") },
                                        leadingIcon = { Icon(Icons.Default.Business, contentDescription = "BusinessIcon") },
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedBorderColor = CyberCyan,
                                            unfocusedBorderColor = Color(0xFF332D44),
                                            focusedTextColor = Color.White,
                                            unfocusedTextColor = Color.White,
                                            focusedLabelColor = CyberCyan,
                                            unfocusedLabelColor = Color(0xFF9E9BA8)
                                        ),
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(bottom = 14.dp)
                                            .testTag("auth_org_input"),
                                        singleLine = true,
                                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done)
                                    )

                                    // Team Role selection matching architectural requirements
                                    Text(
                                        text = "Assign Operations Role",
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 11.sp,
                                        color = CyberCyan,
                                        modifier = Modifier.padding(bottom = 6.dp, top = 4.dp)
                                    )

                                    val roles = listOf("SUPER_ADMIN", "ORG_ADMIN", "ENGINEER", "VIEWER")
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(bottom = 16.dp),
                                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                                    ) {
                                        roles.forEach { role ->
                                            val isSelected = selectedRole == role
                                            Box(
                                                modifier = Modifier
                                                    .weight(1f)
                                                    .clip(RoundedCornerShape(8.dp))
                                                    .background(if (isSelected) Color(0xFF2E2644) else Color(0xFF0F0E13))
                                                    .border(1.dp, if (isSelected) CyberCyan else Color.Transparent, RoundedCornerShape(8.dp))
                                                    .clickable { selectedRole = role }
                                                    .padding(vertical = 8.dp),
                                                contentAlignment = Alignment.Center
                                            ) {
                                                Text(
                                                    text = role.replace("_", "\n"),
                                                    fontSize = 8.sp,
                                                    fontWeight = FontWeight.Bold,
                                                    color = if (isSelected) Color.White else Color(0xFF9E9BA8),
                                                    textAlign = TextAlign.Center,
                                                    lineHeight = 10.sp
                                                )
                                            }
                                        }
                                    }

                                    // SaaS Tier dropdown layout
                                    Text(
                                        text = "SaaS Infrastructure Tier",
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 11.sp,
                                        color = CyberCyan,
                                        modifier = Modifier.padding(bottom = 6.dp)
                                    )

                                    val plans = listOf("BASIC", "PREMIUM", "ENTERPRISE")
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(bottom = 16.dp),
                                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                                    ) {
                                        plans.forEach { plan ->
                                            val isSelected = selectedPlan == plan
                                            Box(
                                                modifier = Modifier
                                                    .weight(1f)
                                                    .clip(RoundedCornerShape(8.dp))
                                                    .background(if (isSelected) Color(0xFF2E2644) else Color(0xFF0F0E13))
                                                    .border(1.dp, if (isSelected) CyberCyan else Color.Transparent, RoundedCornerShape(8.dp))
                                                    .clickable { selectedPlan = plan }
                                                    .padding(vertical = 8.dp),
                                                contentAlignment = Alignment.Center
                                            ) {
                                                Text(
                                                    text = plan,
                                                    fontSize = 10.sp,
                                                    fontWeight = FontWeight.Bold,
                                                    color = if (isSelected) Color.White else Color(0xFF9E9BA8)
                                                )
                                            }
                                        }
                                    }
                                }

                                // Interactive Submission Action
                                Button(
                                    onClick = {
                                        keyboardController?.hide()
                                        if (email.isEmpty() || password.isEmpty()) {
                                            errorMessage = "All directory fields must be populated."
                                            return@Button
                                        }

                                        isLoading = true
                                        errorMessage = null

                                        if (selectedTab == AuthTab.SIGN_IN) {
                                            viewModel.loginUser(email, password,
                                                onCompleted = {
                                                    isLoading = false
                                                    // Trigger Phase 2: MFA verification logic
                                                    currentStage = AuthStage.MFA
                                                },
                                                onError = { err ->
                                                    isLoading = false
                                                    errorMessage = err
                                                }
                                            )
                                        } else {
                                            if (orgName.isEmpty()) {
                                                isLoading = false
                                                errorMessage = "Organization Name is mandatory for registration."
                                                return@Button
                                            }
                                            viewModel.registerUser(email, password, orgName, selectedPlan, selectedRole,
                                                onCompleted = {
                                                    isLoading = false
                                                    // Immediately trigger MFA validation for newly registered admin
                                                    currentStage = AuthStage.MFA
                                                },
                                                onError = { err ->
                                                    isLoading = false
                                                    errorMessage = err
                                                }
                                            )
                                        }
                                    },
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(50.dp)
                                        .testTag("auth_submit_button"),
                                    colors = ButtonDefaults.buttonColors(containerColor = BentoPurplePrimary),
                                    shape = RoundedCornerShape(12.dp),
                                    enabled = !isLoading
                                ) {
                                    if (isLoading) {
                                        CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                                    } else {
                                        Text(
                                            text = if (selectedTab == AuthTab.SIGN_IN) "Initialize Console Link" else "Acknowledge Operator Profile",
                                            fontSize = 13.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = Color.White,
                                            fontFamily = FontFamily.Monospace,
                                        )
                                    }
                                }

                                // Secondary controls
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(top = 16.dp),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(
                                        text = "Forgot Password?",
                                        color = CyberCyan,
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.clickable {
                                            errorMessage = null
                                            currentStage = AuthStage.FORGOT_PASSWORD
                                        }
                                    )
                                    Text(
                                        text = "Demo Key: admin123",
                                        color = Color(0xFF9E9BA8),
                                        fontSize = 11.sp,
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                            }
                        }

                        AuthStage.MFA -> {
                            Column(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = "Phase 2: Multi-Factor Authentication",
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White,
                                    textAlign = TextAlign.Center,
                                    modifier = Modifier.padding(bottom = 6.dp)
                                )
                                Text(
                                    text = "Zero Trust security framework dictates mandatory verification",
                                    fontSize = 11.sp,
                                    color = Color(0xFF9E9BA8),
                                    textAlign = TextAlign.Center,
                                    modifier = Modifier.padding(bottom = 20.dp)
                                )

                                if (mfaStep == 1) {
                                    // select MFA Method
                                    val mfaMethods = listOf(
                                        Triple("EMAIL_OTP", "Email Secure OTP", Icons.Default.Email),
                                        Triple("GOOGLE_AUTH", "Google Authenticator", Icons.Default.Fingerprint),
                                        Triple("MICROSOFT_AUTH", "Microsoft Authenticator", Icons.Default.Shield)
                                    )

                                    mfaMethods.forEach { (type, name, icon) ->
                                        val active = mfaMethod == type
                                        Row(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .padding(bottom = 12.dp)
                                                .clip(RoundedCornerShape(12.dp))
                                                .background(if (active) Color(0xFF241E34) else Color(0xFF0F0E13))
                                                .border(1.dp, if (active) CyberCyan else Color(0xFF2C2A35), RoundedCornerShape(12.dp))
                                                .clickable { mfaMethod = type }
                                                .padding(14.dp),
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Icon(imageVector = icon, contentDescription = name, tint = if (active) CyberCyan else Color.White)
                                            Spacer(modifier = Modifier.width(14.dp))
                                            Text(
                                                text = name,
                                                color = Color.White,
                                                fontSize = 13.sp,
                                                fontWeight = FontWeight.Bold
                                            )
                                        }
                                    }

                                    Button(
                                        onClick = {
                                            mfaStep = 2
                                            Toast.makeText(context, "Verification code dispatched via $mfaMethod schema.", Toast.LENGTH_SHORT).show()
                                        },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(top = 12.dp)
                                            .height(48.dp),
                                        colors = ButtonDefaults.buttonColors(containerColor = CyberCyan)
                                    ) {
                                        Text("Dispatch Authentication Challenge", color = Color(0xFF0D0C10), fontWeight = FontWeight.Bold, fontSize = 12.sp)
                                    }
                                } else {
                                    // Enter challenge Code
                                    Text(
                                        text = "Provide current verification code matching synchronized authenticator key:",
                                        fontSize = 12.sp,
                                        color = Color(0xFF9E9BA8),
                                        textAlign = TextAlign.Center,
                                        modifier = Modifier.padding(bottom = 16.dp)
                                    )

                                    OutlinedTextField(
                                        value = mfaCode,
                                        onValueChange = { mfaCode = it },
                                        label = { Text("Code (e.g. 123456)") },
                                        leadingIcon = { Icon(Icons.Default.Security, contentDescription = "SecurityToken") },
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedBorderColor = CyberCyan,
                                            unfocusedBorderColor = Color(0xFF332D44),
                                            focusedTextColor = Color.White,
                                            unfocusedTextColor = Color.White
                                        ),
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(bottom = 16.dp),
                                        singleLine = true,
                                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                                    )

                                    Button(
                                        onClick = {
                                            if (mfaCode.isEmpty()) {
                                                errorMessage = "Code cannot be empty."
                                                return@Button
                                            }
                                            isLoading = true
                                            // Simulate server verification delay
                                            Toast.makeText(context, "MFA token verified successfully", Toast.LENGTH_SHORT).show()
                                            isLoading = false
                                            onLoginSuccess() // Navigate to main control room panel!
                                        },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(48.dp),
                                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00FF66))
                                    ) {
                                        Text("Acknowledge Credentials", color = Color(0xFF0D0C10), fontWeight = FontWeight.Bold)
                                    }

                                    Spacer(modifier = Modifier.height(14.dp))

                                    Text(
                                        text = "Reset selection path",
                                        color = CyberCyan,
                                        fontSize = 11.sp,
                                        modifier = Modifier
                                            .clickable {
                                                mfaStep = 1
                                                errorMessage = null
                                            }
                                            .padding(4.dp)
                                    )
                                }
                            }
                        }

                        AuthStage.FORGOT_PASSWORD -> {
                            Column(modifier = Modifier.fillMaxWidth()) {
                                Text(
                                    text = "Operator Credentials Recovery",
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White,
                                    modifier = Modifier.padding(bottom = 6.dp)
                                )
                                Text(
                                    text = "Send secure dynamic SRE reset link to your registered corporate directory",
                                    fontSize = 11.sp,
                                    color = Color(0xFF9E9BA8),
                                    modifier = Modifier.padding(bottom = 20.dp)
                                )

                                if (forgotStep == 1) {
                                    OutlinedTextField(
                                        value = forgotEmail,
                                        onValueChange = { forgotEmail = it },
                                        label = { Text("Directory Email") },
                                        leadingIcon = { Icon(Icons.Default.Email, contentDescription = "Forgot Email") },
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedBorderColor = CyberCyan,
                                            unfocusedBorderColor = Color(0xFF332D44),
                                            focusedTextColor = Color.White,
                                            unfocusedTextColor = Color.White
                                        ),
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(bottom = 16.dp),
                                        singleLine = true
                                    )

                                    Button(
                                        onClick = {
                                            if (forgotEmail.isEmpty()) {
                                                errorMessage = "Please input email."
                                                return@Button
                                            }
                                            Toast.makeText(context, "Reset codes dispatched.", Toast.LENGTH_SHORT).show()
                                            forgotStep = 2
                                        },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(48.dp),
                                        colors = ButtonDefaults.buttonColors(containerColor = CyberCyan)
                                    ) {
                                        Text("SRE Challenge Dispatch", color = Color(0xFF0D0C10), fontWeight = FontWeight.Bold)
                                    }
                                } else {
                                    OutlinedTextField(
                                        value = forgotCode,
                                        onValueChange = { forgotCode = it },
                                        label = { Text("6-Digit OTP (e.g. 1234)") },
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedBorderColor = CyberCyan,
                                            unfocusedBorderColor = Color(0xFF332D44),
                                            focusedTextColor = Color.White,
                                            unfocusedTextColor = Color.White
                                        ),
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(bottom = 12.dp),
                                        singleLine = true
                                    )

                                    OutlinedTextField(
                                        value = forgotNewPassword,
                                        onValueChange = { forgotNewPassword = it },
                                        label = { Text("New Encrypted Password") },
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedBorderColor = CyberCyan,
                                            unfocusedBorderColor = Color(0xFF332D44),
                                            focusedTextColor = Color.White,
                                            unfocusedTextColor = Color.White
                                        ),
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(bottom = 16.dp),
                                        singleLine = true,
                                        visualTransformation = PasswordVisualTransformation()
                                    )

                                    Button(
                                        onClick = {
                                            if (forgotCode.isEmpty() || forgotNewPassword.isEmpty()) {
                                                errorMessage = "Fields are requested."
                                                return@Button
                                            }
                                            Toast.makeText(context, "Credentials successfully updated.", Toast.LENGTH_SHORT).show()
                                            forgotStep = 1
                                            currentStage = AuthStage.MAIN
                                        },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(48.dp),
                                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00FF66))
                                    ) {
                                        Text("Execute Reset Sequence", color = Color(0xFF0D0C10), fontWeight = FontWeight.Bold)
                                    }
                                }

                                Spacer(modifier = Modifier.height(14.dp))

                                Text(
                                    text = "Return to Console Link",
                                    color = CyberCyan,
                                    fontSize = 11.sp,
                                    modifier = Modifier
                                        .clickable {
                                            forgotStep = 1
                                            currentStage = AuthStage.MAIN
                                            errorMessage = null
                                        }
                                        .padding(4.dp)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
