package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.terminal.CloudShellViewModel
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CloudShellScreen() {
    val vm: CloudShellViewModel = viewModel()
    var commandInput by remember { mutableStateOf("") }
    var wsUrlInput by remember { mutableStateOf(vm.currentWsUrl) }
    var showSettings by remember { mutableStateOf(false) }
    var fullScreenTerminal by remember { mutableStateOf(false) }

    val coroutineScope = rememberCoroutineScope()
    val focusManager = LocalFocusManager.current

    // Auto-connect on start
    LaunchedEffect(Unit) {
        vm.connect()
    }

    val verticalScrollState = rememberScrollState()
    val horizontalScrollState = rememberScrollState()

    // Auto-scroll when terminal text changes
    LaunchedEffect(vm.terminalModel.terminalText) {
        if (verticalScrollState.maxValue > 0) {
            verticalScrollState.animateScrollTo(verticalScrollState.maxValue)
        }
    }

    // Dynamic terminal resizing effect on fullscreen state change
    LaunchedEffect(fullScreenTerminal) {
        if (fullScreenTerminal) {
            vm.resizeTerminal(cols = 120, rows = 45)
        } else {
            vm.resizeTerminal(cols = 100, rows = 35)
        }
    }

    val activeStatusColor = when {
        vm.connectionStatus.contains("Connected", ignoreCase = true) -> Color(0xFF00FF66)
        vm.connectionStatus.contains("Connecting", ignoreCase = true) -> Color(0xFFFFCC00)
        else -> Color(0xFFFF3366)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(if (fullScreenTerminal) 6.dp else 12.dp)
            .testTag("cloud_shell_screen_root")
    ) {
        // Upper Control / Status Header Card
        ElevatedCard(
            colors = CardDefaults.elevatedCardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
            ),
            shape = RoundedCornerShape(16.dp),
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp)
        ) {
            Column(
                modifier = Modifier.padding(12.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(10.dp)
                                .clip(CircleShape)
                                .background(activeStatusColor)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Status: ${vm.connectionStatus}",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace,
                            color = activeStatusColor
                        )
                    }

                    Row {
                        IconButton(
                            onClick = { fullScreenTerminal = !fullScreenTerminal },
                            modifier = Modifier.size(32.dp)
                        ) {
                            Icon(
                                imageVector = if (fullScreenTerminal) Icons.Default.FullscreenExit else Icons.Default.Terminal,
                                contentDescription = "Toggle Fullscreen Mode",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(4.dp))
                        IconButton(
                            onClick = { vm.connect() },
                            modifier = Modifier.size(32.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Refresh,
                                contentDescription = "Retry Connection",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(4.dp))
                        IconButton(
                            onClick = { showSettings = !showSettings },
                            modifier = Modifier.size(32.dp)
                        ) {
                            Icon(
                                imageVector = if (showSettings) Icons.Default.Close else Icons.Default.Settings,
                                contentDescription = "Shell Settings",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(4.dp))

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = "Region: us-east-1",
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.8f)
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Text(
                        text = "Shell: cloud-shell",
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.8f)
                    )
                }

                if (showSettings) {
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        text = "WebSocket URL",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        OutlinedTextField(
                            value = wsUrlInput,
                            onValueChange = { wsUrlInput = it },
                            modifier = Modifier
                                .weight(1f)
                                .height(52.dp),
                            singleLine = true,
                            textStyle = LocalTextStyle.current.copy(
                                fontSize = 12.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Button(
                            onClick = {
                                vm.connect(wsUrlInput)
                                focusManager.clearFocus()
                            },
                            modifier = Modifier.height(52.dp)
                        ) {
                            Text("Set", fontSize = 12.sp)
                        }
                    }
                }
            }
        }

        // Terminal Output Screen - Upgraded to prevent character clipping or margin truncation
        Card(
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFF0F0E13)
            ),
            shape = RoundedCornerShape(12.dp),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.3f)),
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(start = 10.dp, end = 10.dp, top = 8.dp, bottom = 8.dp)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(verticalScrollState)
                        .horizontalScroll(horizontalScrollState)
                ) {
                    Text(
                        text = vm.terminalModel.terminalText,
                        fontFamily = FontFamily.Monospace,
                        fontSize = 11.sp,
                        lineHeight = 13.sp,
                        softWrap = false
                    )
                }

                // Top-right mini overlay controls
                Row(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(4.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(8.dp))
                            .background(Color.White.copy(alpha = 0.1f))
                            .clickable { vm.clearTerminal() }
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = "CLEAR LOGS",
                            color = Color.LightGray,
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                }
            }
        }

        if (!fullScreenTerminal) {
            Spacer(modifier = Modifier.height(10.dp))

            // Quick Command Shortcuts helper Row
            Text(
                text = "QUIKCOMMANDS MACRO",
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.outline,
                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
            )
            LazyRow(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                val macros = listOf(
                    "aws --version",
                    "aws sts get-caller-identity",
                    "terraform -version",
                    "pwd && ls -la"
                )
                items(macros) { cmd ->
                    SuggestionChip(
                        onClick = {
                            commandInput = cmd
                        },
                        label = {
                            Text(
                                text = cmd,
                                fontSize = 10.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        },
                        modifier = Modifier.height(28.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(6.dp))

            // Interactive Horizontally Scrollable Keys Row
            Text(
                text = "SHELL KEYS & NAVIGATION",
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.outline,
                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
            )
            
            LazyRow(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(5.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                val ctrlKeysList = listOf(
                    Triple("TAB", "\t", true),
                    Triple("ESC", "\u001b", true),
                    Triple("Ctrl+C", "\u0003", true),
                    Triple("Ctrl+D", "\u0004", true),
                    Triple("Ctrl+L", "\u000c", true),
                    Triple("◀", "\u001b[D", false),
                    Triple("▲", "\u001b[A", false),
                    Triple("▼", "\u001b[B", false),
                    Triple("▶", "\u001b[C", false)
                )

                items(ctrlKeysList) { (label, code, isControl) ->
                    FilledTonalButton(
                        onClick = { vm.execute(code) },
                        contentPadding = PaddingValues(horizontal = 10.dp),
                        colors = ButtonDefaults.filledTonalButtonColors(
                            containerColor = if (isControl) {
                                MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.8f)
                            } else {
                                MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.8f)
                            },
                            contentColor = if (isControl) {
                                MaterialTheme.colorScheme.onSurfaceVariant
                            } else {
                                MaterialTheme.colorScheme.onSecondaryContainer
                            }
                        ),
                        modifier = Modifier.height(34.dp)
                    ) {
                        Text(
                            text = label,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                }
            }
        }

        if (!fullScreenTerminal) {
            Spacer(modifier = Modifier.height(8.dp))

            // Command Inputs Row - Optimized to be very compact and elegant
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 6.dp)
            ) {
                OutlinedTextField(
                    value = commandInput,
                    onValueChange = { commandInput = it },
                    placeholder = {
                        Text(
                            "Input standard CLI commands...",
                            fontSize = 11.sp,
                            fontFamily = FontFamily.Monospace
                        )
                    },
                    modifier = Modifier
                        .weight(1f)
                        .height(48.dp)
                        .testTag("terminal_command_input"),
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(
                        imeAction = ImeAction.Send
                    ),
                    keyboardActions = KeyboardActions(
                        onSend = {
                            if (commandInput.isNotEmpty()) {
                                vm.execute(commandInput + "\n")
                                commandInput = ""
                            }
                        }
                    ),
                    textStyle = LocalTextStyle.current.copy(
                        fontSize = 12.sp,
                        fontFamily = FontFamily.Monospace
                    ),
                    leadingIcon = {
                        Text(
                            text = "$",
                            fontFamily = FontFamily.Monospace,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.ExtraBold,
                            color = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.padding(start = 10.dp, end = 2.dp)
                        )
                    },
                    shape = RoundedCornerShape(24.dp)
                )

                Spacer(modifier = Modifier.width(6.dp))

                FloatingActionButton(
                    onClick = {
                        vm.execute(commandInput + "\n")
                        commandInput = ""
                        focusManager.clearFocus()
                    },
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    contentColor = MaterialTheme.colorScheme.onPrimaryContainer,
                    modifier = Modifier
                        .size(44.dp)
                        .testTag("terminal_send_button")
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.Send,
                        contentDescription = "Execute Command",
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }
    }
}
