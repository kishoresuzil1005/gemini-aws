package com.example.terminal

import androidx.compose.runtime.mutableStateListOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight

class TerminalModel(
    val rows: Int = 30,
    val cols: Int = 80
) {
    private val bufferCols = cols
    private val bufferRows = rows
    
    private val grid = Array(bufferRows) { CharArray(bufferCols) { ' ' } }
    private val colors = Array(bufferRows) { LongArray(bufferCols) { 0xFF00FF88 } }
    private val boldState = Array(bufferRows) { BooleanArray(bufferCols) { false } }
    
    var cursorRow = 0
    var cursorCol = 0
    private var activeColor: Long = 0xFF00FF88
    private var isBold = false
    
    private var savedRow = 0
    private var savedCol = 0

    val linesState = mutableStateListOf<AnnotatedString>()

    init {
        clearScreen()
    }

    @Synchronized
    fun clearScreen() {
        for (r in 0 until bufferRows) {
            for (c in 0 until bufferCols) {
                grid[r][c] = ' '
                colors[r][c] = 0xFF00FF88
                boldState[r][c] = false
            }
        }
        cursorRow = 0
        cursorCol = 0
        activeColor = 0xFF00FF88
        isBold = false
        commitToState()
    }

    private fun commitToState() {
        linesState.clear()
        for (r in 0 until bufferRows) {
            val annotated = buildAnnotatedString {
                var currentIndex = 0
                while (currentIndex < bufferCols) {
                    val start = currentIndex
                    val colValue = colors[r][start]
                    val isCellBold = boldState[r][start]
                    
                    while (currentIndex < bufferCols && 
                           colors[r][currentIndex] == colValue && 
                           boldState[r][currentIndex] == isCellBold) {
                        currentIndex++
                    }
                    val textRun = grid[r].concatToString(start, currentIndex)
                    pushStyle(
                        SpanStyle(
                            color = Color(colValue),
                            fontFamily = FontFamily.Monospace,
                            fontWeight = if (isCellBold) FontWeight.Bold else FontWeight.Normal
                        )
                    )
                    append(textRun)
                    pop()
                }
            }
            linesState.add(annotated)
        }
    }

    @Synchronized
    fun writeData(text: String) {
        var i = 0
        val len = text.length
        while (i < len) {
            val char = text[i]
            if (char == '\u001b') {
                if (i + 1 < len) {
                    val nextChar = text[i + 1]
                    if (nextChar == '[') {
                        var j = i + 2
                        val sb = StringBuilder()
                        var commandChar = ' '
                        while (j < len) {
                            val c = text[j]
                            if (c in 'a'..'z' || c in 'A'..'Z' || c == '@' || c == '`' || c == '{' || c == '}' || c == '~') {
                                commandChar = c
                                break
                            } else {
                                sb.append(c)
                            }
                            j++
                        }
                        if (commandChar != ' ') {
                            executeCsiCommand(commandChar, sb.toString())
                            i = j
                        } else {
                            i++
                        }
                    } else if (nextChar == '(' || nextChar == ')') {
                        // Skip charset specification (e.g., \u001b(B)
                        i += 2
                    } else {
                        i++
                    }
                }
            } else {
                when (char) {
                    '\n' -> {
                        cursorRow++
                        if (cursorRow >= bufferRows) {
                            scrollUp()
                            cursorRow = bufferRows - 1
                        }
                    }
                    '\r' -> {
                        cursorCol = 0
                    }
                    '\t' -> {
                        val spaces = 8 - (cursorCol % 8)
                        for (s in 0 until spaces) {
                            writeNormalChar(' ')
                        }
                    }
                    '\b' -> {
                        cursorCol = maxOf(0, cursorCol - 1)
                    }
                    else -> {
                        if (char.code >= 32) {
                            writeNormalChar(char)
                        } else if (char.code == 7) {
                            // Bell, ignore
                        }
                    }
                }
            }
            i++
        }
        commitToState()
    }

    private fun writeNormalChar(char: Char) {
        if (cursorCol >= bufferCols) {
            cursorCol = 0
            cursorRow++
            if (cursorRow >= bufferRows) {
                scrollUp()
                cursorRow = bufferRows - 1
            }
        }
        grid[cursorRow][cursorCol] = char
        colors[cursorRow][cursorCol] = activeColor
        boldState[cursorRow][cursorCol] = isBold
        cursorCol++
    }

    private fun scrollUp() {
        for (r in 0 until bufferRows - 1) {
            for (c in 0 until bufferCols) {
                grid[r][c] = grid[r + 1][c]
                colors[r][c] = colors[r + 1][c]
                boldState[r][c] = boldState[r + 1][c]
            }
        }
        for (c in 0 until bufferCols) {
            grid[bufferRows - 1][c] = ' '
            colors[bufferRows - 1][c] = 0xFF00FF88
            boldState[bufferRows - 1][c] = false
        }
    }

    private fun executeCsiCommand(command: Char, paramsStr: String) {
        val params = paramsStr.replace("?", "").split(';').map { it.toIntOrNull() }
        when (command) {
            'm' -> {
                for (param in params) {
                    val code = param ?: 0
                    when (code) {
                        0 -> {
                            activeColor = 0xFF00FF88
                            isBold = false
                        }
                        1 -> isBold = true
                        22 -> isBold = false
                        30 -> activeColor = 0xFF1E1E1E
                        31 -> activeColor = 0xFFFF5252
                        32 -> activeColor = 0xFF00FF88
                        33 -> activeColor = 0xFFFFD700
                        34 -> activeColor = 0xFF42A5F5
                        35 -> activeColor = 0xFFAB47BC
                        36 -> activeColor = 0xFF26C6DA
                        37 -> activeColor = 0xFFECEFF1
                        39 -> activeColor = 0xFF00FF88
                        
                        90 -> activeColor = 0xFF78909C
                        91 -> activeColor = 0xFFFF8A80
                        92 -> activeColor = 0xFFB9F6CA
                        93 -> activeColor = 0xFFFFE082
                        94 -> activeColor = 0xFF80D8FF
                        95 -> activeColor = 0xFFEA80FC
                        96 -> activeColor = 0xFF84FFFF
                        97 -> activeColor = 0xFFFFFFFF
                    }
                }
            }
            'H', 'f' -> {
                val destRow = if (params.isNotEmpty() && params[0] != null) params[0]!! - 1 else 0
                val destCol = if (params.size > 1 && params[1] != null) params[1]!! - 1 else 0
                cursorRow = destRow.coerceIn(0, bufferRows - 1)
                cursorCol = destCol.coerceIn(0, bufferCols - 1)
            }
            'J' -> {
                val clearMode = if (params.isNotEmpty() && params[0] != null) params[0]!! else 0
                if (clearMode == 2 || clearMode == 3) {
                    for (r in 0 until bufferRows) {
                        for (c in 0 until bufferCols) {
                            grid[r][c] = ' '
                            colors[r][c] = activeColor
                            boldState[r][c] = false
                        }
                    }
                    cursorRow = 0
                    cursorCol = 0
                } else if (clearMode == 0) {
                    for (c in cursorCol until bufferCols) {
                        grid[cursorRow][c] = ' '
                    }
                    for (r in cursorRow + 1 until bufferRows) {
                        for (c in 0 until bufferCols) {
                            grid[r][c] = ' '
                        }
                    }
                }
            }
            'K' -> {
                val clearMode = if (params.isNotEmpty() && params[0] != null) params[0]!! else 0
                if (clearMode == 0) {
                    for (c in cursorCol until bufferCols) {
                        grid[cursorRow][c] = ' '
                    }
                } else if (clearMode == 1) {
                    for (c in 0 until minOf(cursorCol, bufferCols)) {
                        grid[cursorRow][c] = ' '
                    }
                } else if (clearMode == 2) {
                    for (c in 0 until bufferCols) {
                        grid[cursorRow][c] = ' '
                    }
                }
            }
            'A' -> {
                val dist = if (params.isNotEmpty() && params[0] != null) params[0]!! else 1
                cursorRow = maxOf(0, cursorRow - dist)
            }
            'B' -> {
                val dist = if (params.isNotEmpty() && params[0] != null) params[0]!! else 1
                cursorRow = minOf(bufferRows - 1, cursorRow + dist)
            }
            'C' -> {
                val dist = if (params.isNotEmpty() && params[0] != null) params[0]!! else 1
                cursorCol = minOf(bufferCols - 1, cursorCol + dist)
            }
            'D' -> {
                val dist = if (params.isNotEmpty() && params[0] != null) params[0]!! else 1
                cursorCol = maxOf(0, cursorCol - dist)
            }
            's' -> {
                savedRow = cursorRow
                savedCol = cursorCol
            }
            'u' -> {
                cursorRow = savedRow
                cursorCol = savedCol
            }
        }
    }
}
