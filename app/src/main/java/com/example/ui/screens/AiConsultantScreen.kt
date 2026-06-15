package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.SmartToy
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.graphics.Color
import com.example.api.GeminiClient
import com.example.ui.ChatMessage
import com.example.ui.CloudViewModel
import com.example.ui.theme.*

@Composable
fun AiConsultantScreen(
    viewModel: CloudViewModel,
    modifier: Modifier = Modifier
) {
    val messages by viewModel.chatMessages.collectAsState()
    val isGenerating by viewModel.isGeneratingAi.collectAsState()
    var inputQuery by remember { mutableStateOf("") }

    val lazyListState = rememberLazyListState()

    // Auto-scroll to lowest message index as messages grow
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            lazyListState.animateScrollToItem(messages.size - 1)
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(SpaceSlate)
    ) {
        // AI Architect Title Block
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(DeepCard)
                .border(width = 1.dp, color = BorderGrey)
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(CyberCyan.copy(alpha = 0.15f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.AutoAwesome,
                    contentDescription = "AI Icon",
                    tint = CyberCyan,
                    modifier = Modifier.size(22.dp)
                )
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(
                    text = "AMAZON Q MIGRATION ADVISOR",
                    fontSize = 11.sp,
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold,
                    color = CyberCyan
                )
                Text(
                    text = "Cloud Architect AI",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = TextWhite
                )
            }

            Spacer(modifier = Modifier.weight(1f))

            // Alert API Key usage status
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(4.dp))
                    .background(if (GeminiClient.isApiKeyConfigured()) TerminalGreen.copy(alpha = 0.15f) else WarningAmber.copy(alpha = 0.15f))
                    .border(1.dp, if (GeminiClient.isApiKeyConfigured()) TerminalGreen else WarningAmber, RoundedCornerShape(4.dp))
                    .padding(horizontal = 8.dp, vertical = 4.dp)
            ) {
                Text(
                    text = if (GeminiClient.isApiKeyConfigured()) "LIVE Amazon Q" else "Simulated",
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    color = if (GeminiClient.isApiKeyConfigured()) TerminalGreen else WarningAmber
                )
            }
        }

        // Live Chat Feed
        LazyColumn(
            state = lazyListState,
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            contentPadding = PaddingValues(vertical = 16.dp)
        ) {
            items(messages) { message ->
                ChatMessageBubble(message = message)
            }

            // AI Working indicator block
            if (isGenerating) {
                item {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .clip(RoundedCornerShape(6.dp))
                                .background(BorderGrey),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.SmartToy,
                                contentDescription = "Sensing",
                                tint = CyberCyan,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Card(
                            colors = CardDefaults.cardColors(containerColor = DeepCard),
                            border = BorderStroke(1.dp, BorderGrey)
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(14.dp),
                                    strokeWidth = 2.dp,
                                    color = CyberCyan
                                )
                                Spacer(modifier = Modifier.width(10.dp))
                                Text(
                                    text = "Analyzing network graph, referencing databases...",
                                    fontSize = 12.sp,
                                    fontFamily = FontFamily.Monospace,
                                    color = TextDim
                                )
                            }
                        }
                    }
                }
            }
        }

        // Preset Prompt Chips Selector Row
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 4.dp)
        ) {
            val presets = listOf(
                "Explain discovered AWS subnets",
                "Conduct a security vulnerability audit",
                "Optimize EC2 instance billing spend",
                "Write S3 to Azure Blob Terraform code"
            )
            Row(
                modifier = Modifier
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                presets.forEach { preset ->
                    AssistChip(
                        onClick = { viewModel.submitPresetQuery(preset) },
                        label = {
                            Text(
                                text = preset,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = TextWhite
                            )
                        },
                        colors = AssistChipDefaults.assistChipColors(
                            containerColor = DeepCard,
                            labelColor = TextWhite
                        ),
                        border = BorderStroke(1.dp, BorderGrey),
                        shape = RoundedCornerShape(16.dp)
                    )
                }
            }
        }

        // Typing Box Container
        Surface(
            modifier = Modifier.fillMaxWidth().imePadding(),
            tonalElevation = 8.dp,
            border = BorderStroke(1.dp, BorderGrey),
            color = DeepCard
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .navigationBarsPadding()
                    .padding(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextField(
                    value = inputQuery,
                    onValueChange = { inputQuery = it },
                    placeholder = { Text("Ask the Migration Architect...", color = TextDim, fontSize = 14.sp) },
                    modifier = Modifier
                        .weight(1f)
                        .testTag("chat_input_field"),
                    textStyle = LocalTextStyle.current.copy(color = TextWhite, fontSize = 14.sp),
                    colors = TextFieldDefaults.colors(
                        focusedContainerColor = SpaceSlate,
                        unfocusedContainerColor = SpaceSlate,
                        disabledContainerColor = SpaceSlate,
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent
                    ),
                    shape = RoundedCornerShape(8.dp),
                    maxLines = 4
                )
                
                Spacer(modifier = Modifier.width(8.dp))

                IconButton(
                    onClick = {
                        viewModel.sendChatMessage(inputQuery)
                        inputQuery = ""
                    },
                    enabled = inputQuery.isNotBlank() && !isGenerating,
                    modifier = Modifier
                        .size(48.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(if (inputQuery.isNotBlank() && !isGenerating) CyberCyan else BorderGrey)
                        .testTag("chat_send_button")
                ) {
                    Icon(
                        imageVector = Icons.Default.Send,
                        contentDescription = "Send Message",
                        tint = if (inputQuery.isNotBlank() && !isGenerating) SpaceSlate else TextDim,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun ChatMessageBubble(message: ChatMessage) {
    val bubbleShape = if (message.isUser) {
        RoundedCornerShape(12.dp, 12.dp, 4.dp, 12.dp)
    } else {
        RoundedCornerShape(12.dp, 12.dp, 12.dp, 4.dp)
    }

    val containerColor = if (message.isUser) {
        ElectricBlue
    } else {
        DeepCard
    }

    val outlineColor = if (message.isUser) {
        ElectricBlue
    } else {
        BorderGrey
    }

    val textColor = if (message.isUser) {
        Color.White
    } else {
        TextWhite
    }

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (message.isUser) Arrangement.End else Arrangement.Start
    ) {
        if (!message.isUser) {
            Box(
                modifier = Modifier
                    .size(28.dp)
                    .clip(RoundedCornerShape(4.dp))
                    .background(CyberCyan.copy(alpha = 0.2f))
                    .align(Alignment.Top),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.SmartToy,
                    contentDescription = null,
                    tint = CyberCyan,
                    modifier = Modifier.size(14.dp)
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
        }

        Surface(
            modifier = Modifier
                .widthIn(max = 280.dp)
                .border(1.dp, outlineColor, bubbleShape),
            shape = bubbleShape,
            color = containerColor
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                // Styled Text formatter simple markdown parser (titles, codes, bullets)
                MarkdownStyledText(text = message.text, baseColor = textColor)
                
                Spacer(modifier = Modifier.height(4.dp))
                
                Text(
                    text = message.timestamp,
                    fontSize = 9.sp,
                    color = if (message.isUser) Color.White.copy(alpha = 0.7f) else TextDim,
                    fontFamily = FontFamily.Monospace,
                    modifier = Modifier.align(Alignment.End)
                )
            }
        }
    }
}

@Composable
fun MarkdownStyledText(text: String, baseColor: Color) {
    Column {
        val lines = text.split("\n")
        var isInCodeBlock = false
        var codeBlockContent = ""

        lines.forEach { line ->
            when {
                line.trim().startsWith("```") -> {
                    if (isInCodeBlock) {
                        // Close block and render card
                        CodeBlockContainer(code = codeBlockContent)
                        codeBlockContent = ""
                    }
                    isInCodeBlock = !isInCodeBlock
                }
                isInCodeBlock -> {
                    codeBlockContent += line + "\n"
                }
                line.trim().startsWith("###") -> {
                    Text(
                        text = line.replace("###", "").trim(),
                        color = CyberCyan,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.ExtraBold,
                        modifier = Modifier.padding(top = 8.dp, bottom = 4.dp)
                    )
                }
                line.trim().startsWith("*") || line.trim().startsWith("-") -> {
                    Row(modifier = Modifier.padding(start = 6.dp, top = 2.dp)) {
                        Text("• ", color = CyberCyan, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                        Text(
                            text = line.substring(1).trim(),
                            color = baseColor,
                            fontSize = 13.sp,
                            lineHeight = 16.sp
                        )
                    }
                }
                else -> {
                    if (line.isNotEmpty()) {
                        Text(
                            text = line,
                            color = baseColor,
                            fontSize = 13.sp,
                            lineHeight = 17.sp,
                            modifier = Modifier.padding(vertical = 2.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun CodeBlockContainer(code: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
            .clip(RoundedCornerShape(6.dp))
            .background(Color.Black)
            .border(1.dp, BorderGrey, RoundedCornerShape(6.dp))
            .padding(8.dp)
    ) {
        Text(
            text = code.trim(),
            fontFamily = FontFamily.Monospace,
            fontSize = 10.sp,
            lineHeight = 13.sp,
            color = TerminalGreen
        )
    }
}
