import os
import pygame
from pygame.locals import *
import random

# =============================================================================
# CONSTANTS
# =============================================================================

# --- Screen ---
SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 1000
FPS           = 60
TITLE         = "THE-SYNTAX-ESCAPE"

# --- World ---
TILE_SIZE = 40


# --- Game States ---
MENU    = 0
PLAYING = 1
QUIZ    = 2
WIN     = 3
PAUSED  = 4
WORLD_MAP = 5

# --- Tile IDs ---
TILE_BLOCK = 1
TILE_GRASS = 2
TILE_ROCK  = 3
TILE_ENEMY = 4
TILE_GATE  = 5

# --- Colours ---
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = (0,   255, 0)
DARK   = (20,  20,  20)
GOLD   = (255, 215, 0)
CYAN       = (0,   210, 210)   
NEON_GREEN = (0,   220, 100)  

PLAYER_ACCEL     = 1.2    
PLAYER_FRICTION  = 0.70   
PLAYER_MAX_SPEED = 7      
PLAYER_JUMP      = -17    
PLAYER_GRAV_UP   = 1.2    
PLAYER_GRAV_DOWN = 2.6    
PLAYER_MAX_FALL  = 22     
MAX_HP = 5

QUIZ_QUESTIONS = {
    "Python": [
        {"q": "Which keyword defines a function in Python?",
        "options": ["def", "fun", "function", "define"], "answer": 0},
        {"q": "How do you print output in Python?",
        "options": ["print()", "echo()", "console.log()", "printf()"], "answer": 0},
        {"q": "Which creates an empty list?",
        "options": ["[]", "{}", "()", "list{}"], "answer": 0},
        {"q": "How do you add an item to a list?",
        "options": [".append()", ".add()", ".push()", ".insert()"], "answer": 0},
        {"q": "Which is the correct comment syntax?",
         "options": ["# comment", "// comment", "/* comment */", "-- comment"], "answer": 0},
        {"q": "What does len([1,2,3]) return?",
        "options": ["3", "2", "4", "0"], "answer": 0},
        {"q": "Which keyword starts a loop over a list?",
        "options": ["for x in", "foreach x", "loop x in", "each x of"], "answer": 0},
        {"q": "How do you check equality in Python?",
        "options": ["==", "=", "===", ":="], "answer": 0},
        {"q": "Which creates a dictionary?",
        "options": ["{}", "[]", "()", "<>"], "answer": 0},
        {"q": "What keyword skips to the next loop iteration?",
        "options": ["continue", "skip", "next", "pass"], "answer": 0},
    ],
    "Java": [
        {"q": "Which keyword declares a constant in Java?",
        "options": ["final", "const", "static", "fixed"], "answer": 0},
        {"q": "Correct way to print in Java?",
        "options": ["System.out.println()", "print()", "console.log()", "echo()"], "answer": 0},
        {"q": "Which is the correct main method signature?",
        "options": ["public static void main(String[] args)", "void main()", "static main()", "public main(String args)"], "answer": 0},
        {"q": "How do you create an object in Java?",
        "options": ["new ClassName()", "create ClassName()", "make ClassName()", "ClassName.new()"], "answer": 0},
        {"q": "Which keyword handles exceptions?",
        "options": ["try/catch", "attempt/handle", "check/error", "begin/rescue"], "answer": 0},
        {"q": "What is the correct way to declare an int?",
        "options": ["int x = 5;", "x = 5;", "integer x = 5;", "var x = 5;"], "answer": 0},
        {"q": "Which access modifier is most restrictive?",
        "options": ["private", "public", "protected", "internal"], "answer": 0},
        {"q": "How do you extend a class in Java?",
        "options": ["extends", "inherits", "implements", "uses"], "answer": 0},
    ],
    "JavaScript": [
        {"q": "Which keyword declares a block-scoped variable?",
        "options": ["let", "var", "dim", "int"], "answer": 0},
        {"q": "How do you write an arrow function?",
        "options": ["() => {}", "() -> {}", "fn() {}", "lambda() {}"], "answer": 0},
        {"q": "Which method adds to end of an array?",
        "options": [".push()", ".append()", ".add()", ".insert()"], "answer": 0},
        {"q": "Correct way to print to console?",
        "options": ["console.log()", "print()", "System.out.println()", "echo()"], "answer": 0},
        {"q": "Which checks strict equality?",
        "options": ["===", "==", "=", "equals()"], "answer": 0},
        {"q": "How do you declare a constant?",
        "options": ["const", "final", "fixed", "let"], "answer": 0},
        {"q": "Which loops over array elements?",
        "options": ["forEach()", "forAll()", "each()", "loop()"], "answer": 0},
        {"q": "How do you create a Promise?",
        "options": ["new Promise()", "Promise.create()", "async()", "await()"], "answer": 0},
    ],
    "HTML": [
        {"q": "Which tag creates a hyperlink?",
        "options": ["<a>", "<link>", "<href>", "<url>"], "answer": 0},
        {"q": "Which is the correct DOCTYPE for HTML5?",
        "options": ["<!DOCTYPE html>", "<!DOCTYPE HTML5>", "<html>", "<!HTML>"], "answer": 0},
        {"q": "Which tag creates a paragraph?",
        "options": ["<p>", "<para>", "<pg>", "<txt>"], "answer": 0},
        {"q": "Which tag is used for the largest heading?",
        "options": ["<h1>", "<h6>", "<head>", "<title>"], "answer": 0},
        {"q": "How do you insert an image?",
        "options": ["<img src=''>", "<image src=''>", "<pic href=''>", "<src img=''>"], "answer": 0},
        {"q": "Which attribute links CSS to HTML?",
        "options": ["<link rel='stylesheet'>", "<style src=''>", "<css href=''>", "<import css=''>"], "answer": 0},
        {"q": "Which tag creates an unordered list?",
        "options": ["<ul>", "<ol>", "<li>", "<list>"], "answer": 0},
        {"q": "Which tag makes text bold?",
        "options": ["<b> or <strong>", "<bold>", "<thick>", "<em>"], "answer": 0},
    ],
    "CSS": [
        {"q": "How do you select an element with id 'box'?",
        "options": ["#box", ".box", "box", "*box"], "answer": 0},
        {"q": "Which property changes text color?",
        "options": ["color", "text-color", "font-color", "foreground"], "answer": 0},
        {"q": "How do you center a block element?",
        "options": ["margin: 0 auto", "align: center", "center: block", "position: center"], "answer": 0},
        {"q": "Which property controls spacing inside an element?",
        "options": ["padding", "margin", "border", "spacing"], "answer": 0},
        {"q": "How do you make text bold in CSS?",
        "options": ["font-weight: bold", "text-weight: bold", "font-style: bold", "text-bold: true"], "answer": 0},
        {"q": "Which display value makes elements sit side by side?",
        "options": ["flex", "block", "inline-block", "Both C and B"], "answer": 2},
        {"q": "Which unit is relative to viewport width?",
        "options": ["vw", "px", "em", "rem"], "answer": 0},
        {"q": "How do you apply a class selector?",
        "options": [".classname", "#classname", "classname", "@classname"], "answer": 0},
    ],
}

# =============================================================================
# WORLD DATA
# =============================================================================

# fmt: off
WORLD_DATA = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
# fmt: on
WORLD_DATA1 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gate
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # enemy
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0],
    [2,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,0,2,2],
    [1,1,0,0,0,0,0,1,0,1,0,1,0,0,0,1,0,1,0,0,0,0,0,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
WORLD_DATA2 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0],  # gate
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0],  # enemy
    [2,2,2,0,2,0,2,0,2,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
WORLD_DATA3 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [3,3,3,0,3,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,3,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,3,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,3],  # gate
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,3,3,3],
    [0,0,0,0,0,0,0,0,0,2,0,3,0,3,0,3,0,3,0,3,3,3,3,3,3],  # enemy
    [2,0,0,0,0,0,0,0,2,1,0,0,0,0,0,0,0,0,0,3,3,3,3,3,3],
    [1,2,0,0,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,3,3,3,3,3,3],
    [1,1,2,0,0,0,2,1,1,1,0,0,0,0,0,0,0,0,0,3,3,3,3,3,3],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
WORLD_DATA4 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gate
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # enemy
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,5,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
WORLD_DATA5 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0,0],  # gate
    [0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,2,2,2,2,2,2],
    [0,0,0,0,0,0,0,0,0,3,0,2,2,2,0,2,0,2,0,1,1,1,1,1,1],  # enemy
    [2,2,0,3,0,4,0,3,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,1],
    [1,1,0,0,3,3,3,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
WORLD_DATA6 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,5,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [2,2,2,2,2,2,2,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,3,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,3,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,3,0,0,0,3,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,0,3,0,0,0,0,0,0,0,3],  # gate
    [0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,3,0,0,0,0,0,3,3,3],
    [0,0,0,0,0,0,0,0,2,0,3,0,0,4,0,0,3,0,0,0,0,3,3,3,3],  # enemy
    [0,0,0,0,0,0,2,0,0,0,3,0,2,2,2,2,3,0,0,0,3,3,3,3,3],
    [0,0,0,0,2,0,0,0,0,0,3,0,0,0,0,0,0,0,0,3,3,3,3,3,3],
    [0,0,2,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,3,3,3,3,3,3,3],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
WORLD_DATA7 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gate
    [0,0,0,0,0,0,0,0,4,0,0,0,0,3,0,3,0,0,0,0,0,0,0,0,0],
    [2,2,2,2,2,0,2,2,2,2,2,0,0,3,0,0,0,0,0,0,0,0,0,0,0],  # enemy
    [1,1,1,1,1,0,0,0,0,0,0,0,0,3,0,0,0,3,0,0,0,0,0,0,0],
    [1,1,1,1,1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,0,4,0,4,0,4,0,0,3,0,0,0,0,0,3,0,0,0,5,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
WORLD_DATA8 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # gate
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # enemy
    [0,0,0,0,0,0,0,0,0,0,0,4,4,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,3,3,3,3,3,3,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,4,0,4,0,0,3,3,3,3,3,3,0,4,0,4,0,0,0,0,5,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
WORLD_DATA9 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,3,3,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,2,2,0,3,0,3,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,3,0,0,3,3,0],
    [2,2,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0],
    [1,1,0,2,0,2,0,2,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0],
    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,3,3],
    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,3,0,0],  # gate
    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,3,0,0,0],
    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0],  # enemy
    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0],
    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,0,0,0,0],
    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,3,0,5,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
WORLD_DATA10 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [3,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,3,3,3,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,3,0,0,0,0,4,0,4,0,4,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,3,0,3,3,3,3,3,3,3,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,4,0,0,0,3,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,3,3,3,0,3,0,0],  # gate
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,3,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,3,0,0,0,0],  # enemy
    [2,2,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,3,0,0,0,0],
    [1,1,0,2,0,2,0,2,0,1,1,0,0,0,0,0,0,0,0,0,3,0,0,0,0],
    [1,1,0,0,4,0,4,0,0,1,1,0,0,4,0,4,0,4,0,0,3,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# =============================================================================
# WORLD LEVELS LIST
# =============================================================================

WORLD_DATA_LEVELS = [
    WORLD_DATA,    # Level 0
    WORLD_DATA1,   # Level 1  
    WORLD_DATA2,   # Level 2
    WORLD_DATA3,   # Level 3
    WORLD_DATA4,   # Level 4
    WORLD_DATA5,   # Level 5
    WORLD_DATA6,   # Level 6
    WORLD_DATA7,   # Level 7
    WORLD_DATA8,   # Level 8
    WORLD_DATA9,   # Level 9
    WORLD_DATA10,  # Level 10 (note: you have WORLD_DATA9 and WORLD_DATA10)
]

def get_slime_spawn_positions(world_data):
    """Get slime spawn positions for any level."""
    return [
        (col * TILE_SIZE, row * TILE_SIZE)
        for row, tiles in enumerate(world_data)
        for col, tile in enumerate(tiles)
        if tile == TILE_ENEMY
    ]


# =============================================================================
# HELPERS
# =============================================================================

def load_scaled_image(path: str, size: tuple) -> pygame.Surface:
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)


# =============================================================================
# GATE
# ============================================================A=================

class Gate(pygame.sprite.Sprite):
    FRAME_COLS   = 4
    ANIM_SPEED   = 0.08
    DISPLAY_SIZE = (80, 80)

    def __init__(self, x: int, y: int):
        super().__init__()
        self.frames      = self._load_frames()
        self.frame_index = 0.0
        self.image       = self.frames[0]
        self.rect        = self.image.get_rect(bottomleft=(x, y + TILE_SIZE + 2))
        self.hitbox      = self.rect.inflate(-20, -10)
        self.is_opening  = False
        self.is_open     = False

    def _load_frames(self) -> list[pygame.Surface]:
        sheet   = pygame.image.load("GRAPHICS/OTHERS/GATE.png").convert_alpha()
        frame_w = sheet.get_width() // self.FRAME_COLS
        frame_h = sheet.get_height()
        return [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)),
                self.DISPLAY_SIZE,
            )
            for i in range(self.FRAME_COLS)
        ]

    def trigger(self) -> None:
        if not self.is_opening and not self.is_open:
            self.is_opening = True

    def reset(self) -> None:
        self.is_opening  = False
        self.is_open     = False
        self.frame_index = 0.0
        self.image       = self.frames[0]

    def update(self) -> None:
        if not self.is_opening:
            return
        self.frame_index += self.ANIM_SPEED
        if self.frame_index >= len(self.frames):
            self.frame_index = len(self.frames) - 1
            self.is_opening  = False
            self.is_open     = True
        self.image = self.frames[int(self.frame_index)]

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)


# =============================================================================
# BACKGROUND MANAGER
# =============================================================================

class BackgroundManager:
    SWITCH_INTERVAL = 10_000
    LAYER_SPEEDS    = [0.1, 0.2, 0.3, 0.4, 0.5]

    def __init__(self):
        self.day_images   = []
        self.night_images = []

        for i in range(1, 6):
            try:
                self.day_images.append(
                    load_scaled_image(f"GRAPHICS/BACKGROUND/1/Day/{i}.png",   (SCREEN_WIDTH, SCREEN_HEIGHT))
                )
                self.night_images.append(
                    load_scaled_image(f"GRAPHICS/BACKGROUND/1/Night/{i}.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
                )
            except FileNotFoundError:
                pass

        self.is_day      = True
        self.last_switch = pygame.time.get_ticks()
        self.scroll      = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_switch > self.SWITCH_INTERVAL:
            self.is_day      = not self.is_day
            self.last_switch = now

        layers        = self.day_images if self.is_day else self.night_images
        self.scroll  += 2.0

        for img, speed in zip(layers, self.LAYER_SPEEDS):
            # FIX 7: round to int — eliminates sub-pixel shimmer on background layers
            x_offset = round((self.scroll * speed) % SCREEN_WIDTH)
            screen.blit(img, (-x_offset, 0))
            screen.blit(img, (SCREEN_WIDTH - x_offset, 0))


# =============================================================================
# PLAYER
# =============================================================================

class Player(pygame.sprite.Sprite):

    ANIMATION_SPEED  = 0.10
    IDLE_WAIT_MS     = 5_000
    DEATH_DELAY_MS   = 1_000
    RESPAWN_GRACE_MS = 1_000

    def __init__(self, x: int, y: int):
        super().__init__()

        self.animations   = {"IDLE": [], "RUN": [], "JUMP": []}
        self.status       = "STAND"
        self.frame_index  = 0.0
        self.facing_right = True
        self.hp           = MAX_HP
        self.max_hp       = MAX_HP
        self.quiz_trigger_slime = None 

        self._load_animations()

        self.image  = self.animations["IDLE"][0] if self.animations["IDLE"] else pygame.Surface((64, 64))
        self.rect   = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-28, -5)

        # FIX: Track the floating-point position of the HITBOX, not the rect
        self.pos_x = float(self.hitbox.x)
        self.pos_y = float(self.hitbox.y)

        self.vel_x     = 0.0
        self.vel_y     = 0.0
        self.jumped    = False
        self.on_ground = False

        self.is_dying         = False
        self.death_time       = 0
        self.respawn_time     = 0
        self.last_action_time = pygame.time.get_ticks()
        self.is_playing_idle  = False
        

    # ------------------------------------------------------------------
    def _load_animations(self) -> None:
        base = "GRAPHICS/PLAYER/"
        for name in self.animations:
            folder = os.path.join(base, name)
            try:
                for filename in sorted(os.listdir(folder)):
                    if filename.lower().endswith(".png"):
                        img = pygame.image.load(os.path.join(folder, filename)).convert_alpha()
                        self.animations[name].append(pygame.transform.scale(img, (64, 64)))
            except FileNotFoundError:
                print(f"[Player] Animation folder not found: {folder}")

    # ------------------------------------------------------------------
    def _animate(self) -> None:
        if self.status == "STAND":
            if self.animations["IDLE"]:
                self.image = self.animations["IDLE"][0]
            return

        frames = self.animations.get(self.status, [])
        if not frames:
            self.image = pygame.Surface((64, 64))
            return

        self.frame_index += self.ANIMATION_SPEED
        if self.frame_index >= len(frames):
            if self.status == "IDLE":
                self.is_playing_idle  = False
                self.status           = "STAND"
                self.frame_index      = 0.0
                self.last_action_time = pygame.time.get_ticks()
            else:
                self.frame_index = 0.0

        self.image = frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    # ------------------------------------------------------------------
    def _get_input(self) -> bool:
        """
        FIX 3: Accelerate toward max speed while a key is held; bleed speed
        via friction when no key is held.  Returns True if any action taken.
        """
        keys         = pygame.key.get_pressed()
        action_taken = False

        if keys[pygame.K_LEFT]:
            self.vel_x        = max(self.vel_x - PLAYER_ACCEL, -PLAYER_MAX_SPEED)
            self.facing_right = False
            action_taken      = True
        elif keys[pygame.K_RIGHT]:
            self.vel_x        = min(self.vel_x + PLAYER_ACCEL,  PLAYER_MAX_SPEED)
            self.facing_right = True
            action_taken      = True
        else:
            # Friction — bleed horizontal speed to zero
            self.vel_x *= PLAYER_FRICTION
            if abs(self.vel_x) < 0.15:
                self.vel_x = 0.0

        # Update run/stand status based on speed
        if abs(self.vel_x) > 0.5 and self.on_ground:
            self.status  = "RUN"
            action_taken = True

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground and not self.jumped:
            self.vel_y   = PLAYER_JUMP
            self.jumped  = True
            self.status  = "JUMP"
            action_taken = True

        if not keys[pygame.K_SPACE]:
            self.jumped = False

        return action_taken

    # ------------------------------------------------------------------
    def _apply_physics(self, world) -> None:
        grav        = PLAYER_GRAV_UP if self.vel_y < 0 else PLAYER_GRAV_DOWN
        self.vel_y  = min(self.vel_y + grav, PLAYER_MAX_FALL)
        self.on_ground = False

        # --- Horizontal ---
        self.pos_x += self.vel_x
        self.hitbox.x = round(self.pos_x)   

        # FIX: Use hitbox for collision
        for _, tile_rect in world.tile_list:
            if tile_rect.colliderect(self.hitbox):
                if self.vel_x > 0:
                    self.hitbox.right = tile_rect.left
                elif self.vel_x < 0:
                    self.hitbox.left  = tile_rect.right
                self.pos_x = float(self.hitbox.x)
                self.vel_x = 0.0

        # --- Vertical ---
        self.pos_y += self.vel_y
        self.hitbox.y = round(self.pos_y)   

        # FIX: Use hitbox for collision
        for _, tile_rect in world.tile_list:
            if tile_rect.colliderect(self.hitbox):
                if self.vel_y < 0:
                    self.hitbox.top  = tile_rect.bottom
                    self.pos_y       = float(self.hitbox.y)
                    self.vel_y       = 0.0
                else:
                    self.hitbox.bottom = tile_rect.top
                    self.pos_y       = float(self.hitbox.y)
                    self.vel_y       = 0.0
                    self.on_ground   = True
                    self.jumped      = False
                    if abs(self.vel_x) < 0.5:
                        self.status = "STAND"

        # FIX: Sync the visual rect strictly to the physical hitbox center
        self.rect.center = self.hitbox.center

    # ------------------------------------------------------------------
    def update(self, world, game_over: int, slime_group) -> int:
        if game_over != 0:
            self._animate()
            return game_over

        if self.is_dying:
            if pygame.time.get_ticks() - self.death_time > self.DEATH_DELAY_MS:
                return -1
            self._animate()
            return game_over

        now          = pygame.time.get_ticks()
        in_grace     = (now - self.respawn_time) < self.RESPAWN_GRACE_MS
        action_taken = self._get_input()

        if not action_taken and self.on_ground:
            if self.is_playing_idle:
                self.status = "IDLE"
            elif now - self.last_action_time > self.IDLE_WAIT_MS:
                self.is_playing_idle = True
                self.frame_index     = 0.0
                self.status          = "IDLE"
        elif action_taken:
            self.last_action_time = now
            self.is_playing_idle  = False

        self._apply_physics(world)

        if not in_grace and self.quiz_trigger_slime is None:
            for slime in slime_group:
                if self.hitbox.colliderect(slime.hitbox):
                    self.quiz_trigger_slime = slime
                    break

        self._animate()
        return game_over

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, (self.rect.x, self.rect.y + 11))


# =============================================================================
# WORLD
# =============================================================================

class World:
    TILE_IMAGES = {
        TILE_BLOCK: "GRAPHICS/TILES/Tile_02.png",
        TILE_GRASS: "GRAPHICS/TILES/Tile_01.png",
        TILE_ROCK:  "GRAPHICS/TILES/Tile_03.png",
    }

    def __init__(self, data: list[list[int]], difficulty: int, slime_group: pygame.sprite.Group):
        self.tile_list  = []
        self.gate_group = pygame.sprite.Group()
        self.difficulty = difficulty

        tile_surfaces = {
            tid: pygame.transform.scale(
                pygame.image.load(path).convert_alpha(), (TILE_SIZE, TILE_SIZE)
            )
            for tid, path in self.TILE_IMAGES.items()
        }

        for row_idx, row in enumerate(data):
            for col_idx, tile_id in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                if tile_id in tile_surfaces:
                    img = tile_surfaces[tile_id]
                    self.tile_list.append((img, img.get_rect(topleft=(x, y))))
                elif tile_id == TILE_ENEMY:
                    for _ in range(difficulty):
                        slime_group.add(Enemy(x, y))
                elif tile_id == TILE_GATE:
                    self.gate_group.add(Gate(x, y))

    def draw(self, screen: pygame.Surface) -> None:
        for img, rect in self.tile_list:
            screen.blit(img, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
        for gate in self.gate_group:
            gate.draw(screen)

# =============================================================================
# WORLD MAP SCREEN
# =============================================================================

class WorldMapScreen:
    """
    Hacker / glitch-themed level select.
    Matrix rain  ·  scanlines  ·  glitch slices  ·  circuit-board node path
    """
    NODE_RADIUS  = 32
    COLS_PER_ROW = 5
    MATRIX_CHARS = "アイウエオ0123456789ABCDEF<>{}[]|\\/#@!?01"

    def __init__(self, total_levels: int = 10):
        self.total_levels = total_levels
        self.font        = PixelFont(22)
        self.title_font  = PixelFont(36)
        self.small_font  = PixelFont(10)

        # Matrix rain columns
        col_count = SCREEN_WIDTH // 20
        self.rain_cols = [
            {"x": i * 20,
             "y": random.randint(-SCREEN_HEIGHT, 0),
             "speed":  random.randint(3, 8),
             "length": random.randint(8, 20)}
            for i in range(col_count)
        ]

        # Glitch state
        self.glitch_active   = False
        self.glitch_timer    = 0
        self.glitch_cooldown = 0
        self.glitch_slices   = []

        # Title twitch
        self._title_dx    = 0
        self._title_tick  = 0

        # Scanline overlay (built once)
        self._scanlines = self._make_scanlines()

        # Node layout
        self._node_pos = self._compute_nodes()

        # Click flash
        self._flash_node : int | None = None
        self._flash_time : int        = 0

        # Sys-font for matrix characters
        self._mfont = pygame.font.SysFont("courier", 16, bold=True)

        # Back button
        self._back_rect = pygame.Rect(30, 30, 140, 40)

    # ------------------------------------------------------------------
    def _make_scanlines(self):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 3):
            pygame.draw.line(surf, (0, 0, 0, 55), (0, y), (SCREEN_WIDTH, y))
        return surf

    def _compute_nodes(self):
        positions = []
        margin_x  = 120
        margin_y  = 280
        spacing_x = (SCREEN_WIDTH - 2 * margin_x) // (self.COLS_PER_ROW - 1)
        spacing_y = 260
        for i in range(self.total_levels):
            row = i // self.COLS_PER_ROW
            col = i  % self.COLS_PER_ROW
            if row % 2 == 1:            # snake: right-to-left on even row index
                col = self.COLS_PER_ROW - 1 - col
            x = margin_x + col * spacing_x
            y = margin_y + row * spacing_y
            positions.append((x, y))
        return positions

    def _trigger_glitch(self):
        self.glitch_slices = [
            (random.randint(0, SCREEN_HEIGHT - 40),
             random.randint(4, 28),
             random.randint(-25, 25),
             random.choice([(255,0,0,35),(0,255,255,35),(255,255,0,25)]))
            for _ in range(random.randint(2, 5))
        ]
        self.glitch_active   = True
        self.glitch_timer    = random.randint(3, 7)
        self.glitch_cooldown = random.randint(60, 200)

    # ------------------------------------------------------------------
    def update(self):
        # Rain
        for col in self.rain_cols:
            col["y"] += col["speed"]
            if col["y"] > SCREEN_HEIGHT + col["length"] * 18:
                col["y"]      = random.randint(-200, -20)
                col["speed"]  = random.randint(3, 8)
                col["length"] = random.randint(8, 20)

        # Glitch trigger
        if self.glitch_cooldown > 0:
            self.glitch_cooldown -= 1
        elif random.random() < 0.02:
            self._trigger_glitch()
        if self.glitch_active:
            self.glitch_timer -= 1
            if self.glitch_timer <= 0:
                self.glitch_active = False

        # Title twitch
        self._title_tick -= 1
        if self._title_tick <= 0:
            self._title_dx   = random.randint(-6, 6) if random.random() < 0.25 else 0
            self._title_tick = random.randint(4, 20)

    # ------------------------------------------------------------------
    def _dashed_line(self, screen, color, p1, p2, dash=14, gap=7, w=2):
        dx, dy = p2[0]-p1[0], p2[1]-p1[1]
        length = max(1, (dx*dx + dy*dy)**0.5)
        ux, uy = dx/length, dy/length
        pos, draw = 0, True
        while pos < length:
            seg = dash if draw else gap
            x1 = p1[0] + ux * pos;         y1 = p1[1] + uy * pos
            x2 = p1[0] + ux * min(pos+seg, length)
            y2 = p1[1] + uy * min(pos+seg, length)
            if draw:
                pygame.draw.line(screen, color,
                                 (round(x1), round(y1)),
                                 (round(x2), round(y2)), w)
            pos += seg;  draw = not draw

    def _node_rect(self, i):
        cx, cy = self._node_pos[i]
        r = self.NODE_RADIUS + 8
        return pygame.Rect(cx - r, cy - r, r*2, r*2)

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface, mouse_pos: tuple,
             highest_unlocked: int) -> None:
        screen.fill((2, 8, 2))

        # ── Matrix rain ──────────────────────────────────────────────
        for col in self.rain_cols:
            for i in range(col["length"]):
                cy = col["y"] - i * 18
                if cy < 0 or cy > SCREEN_HEIGHT:
                    continue
                ch = random.choice(self.MATRIX_CHARS)
                if i == 0:
                    color = (200, 255, 200)
                elif i < 3:
                    color = (0, 220, 80)
                else:
                    color = (0, max(30, 110 - i*7), 0)
                screen.blit(self._mfont.render(ch, True, color), (col["x"], cy))

        # ── Dark overlay ─────────────────────────────────────────────
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 155))
        screen.blit(ov, (0, 0))

        # ── Glitch slices ────────────────────────────────────────────
        if self.glitch_active:
            for (gy, gh, goff, gcol) in self.glitch_slices:
                band = pygame.Surface((SCREEN_WIDTH, gh), pygame.SRCALPHA)
                band.fill(gcol)
                screen.blit(band, (0, gy))
                safe_w = SCREEN_WIDTH - abs(goff)
                if safe_w > 0 and gh > 0:
                    try:
                        sl = screen.subsurface(
                            pygame.Rect(0, gy, safe_w, gh)).copy()
                        screen.blit(sl, (goff, gy))
                    except ValueError:
                        pass

        # ── Scanlines ────────────────────────────────────────────────
        screen.blit(self._scanlines, (0, 0))

        # ── Title ────────────────────────────────────────────────────
        title = "// WORLD MAP //"
        tw    = self.title_font.text_width(title)
        tx    = SCREEN_WIDTH // 2 - tw // 2 + self._title_dx
        ty    = 40
        if self._title_dx != 0:
            # Red ghost offset
            self.title_font.render(title, screen, tx + 4, ty, color=WHITE)
        self.title_font.render(title, screen, tx, ty, color=WHITE)
        line_y = ty + self.title_font.glyph_size + 10
        pygame.draw.line(screen, (0, 255, 100), (60, line_y),(SCREEN_WIDTH - 60, line_y), 2)

        # ── Path connectors ──────────────────────────────────────────
        for i in range(len(self._node_pos) - 1):
            x1, y1 = self._node_pos[i]
            x2, y2 = self._node_pos[i + 1]
            unlocked_next = (i + 2) <= highest_unlocked
            color = (0, 180, 80) if unlocked_next else (30, 55, 30)
            self._dashed_line(screen, color, (x1, y1), (x2, y2))

        # ── Nodes ────────────────────────────────────────────────────
        now = pygame.time.get_ticks()
        for i, (cx, cy) in enumerate(self._node_pos):
            lvl       = i + 1
            unlocked  = lvl <= highest_unlocked
            hovered   = unlocked and self._node_rect(i).collidepoint(mouse_pos)
            flashing  = (self._flash_node == i and
                         now - self._flash_time < 150)

            # Pulse ring on highest reached node
            if unlocked and lvl == highest_unlocked:
                pulse = abs((now % 1200) - 600) / 600
                pr    = int(self.NODE_RADIUS + 6 + pulse * 8)
                ps    = pygame.Surface((pr*2+4, pr*2+4), pygame.SRCALPHA)
                pygame.draw.circle(ps, (0, 255, 80, int(70 * pulse)),
                                   (pr+2, pr+2), pr, 2)
                screen.blit(ps, (cx - pr - 2, cy - pr - 2))

            # Fill + ring
            fill = ((0, 255, 150) if flashing
                    else (0, 55, 28) if hovered
                    else (0, 25, 12) if unlocked
                    else (8, 12, 8))
            ring = ((255, 255, 255) if flashing
                    else (0, 255, 100) if hovered
                    else (0, 200, 80) if unlocked
                    else (35, 55, 35))

            pygame.draw.circle(screen, fill, (cx, cy), self.NODE_RADIUS)
            pygame.draw.circle(screen, ring, (cx, cy), self.NODE_RADIUS, 3)

            # Corner brackets on unlocked nodes
            if unlocked:
                br   = self.NODE_RADIUS + 7
                blen = 10
                bc   = (0, 255, 100) if hovered else (0, 140, 55)
                for sx, sy, dx, dy in [
                    (-1, -1,  1,  0), (-1, -1,  0,  1),
                    ( 1, -1, -1,  0), ( 1, -1,  0,  1),
                    (-1,  1,  1,  0), (-1,  1,  0, -1),
                    ( 1,  1, -1,  0), ( 1,  1,  0, -1),
                ]:
                    ox, oy = cx + sx*br, cy + sy*br
                    pygame.draw.line(screen, bc,
                                     (ox, oy), (ox + dx*blen, oy + dy*blen), 2)

            # Level number
            lbl = str(lvl)
            lw  = self.font.text_width(lbl)
            tc  = (0, 255, 120) if unlocked else (35, 60, 35)
            self.font.render(lbl, screen, cx - lw//2, cy - self.font.glyph_size//2, color=WHITE)
            
            # Padlock on locked nodes
            if not unlocked:
                pygame.draw.rect(screen, (40, 65, 40),(cx - 7, cy + 2, 14, 11))
                pygame.draw.arc(screen, (40, 65, 40),
                                pygame.Rect(cx - 6, cy - 8, 12, 14),
                                0, 3.14159, 2)

        # ── Back button ──────────────────────────────────────────────
        bh = self._back_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen,(0, 180, 70) if bh else (0, 80, 30),self._back_rect, 2)
        bl = self.small_font.text_width("< MAIN MENU")
        self.small_font.render("< MAIN MENU", screen,self._back_rect.centerx - bl//2,self._back_rect.centery - self.small_font.glyph_size//2,color=WHITE)

    # ------------------------------------------------------------------
    def handle_click(self, pos, highest_unlocked: int):
        """
        Returns level number (1-based) if a node was clicked,
        0 if Back was clicked, None otherwise.
        """
        if self._back_rect.collidepoint(pos):
            return 0
        for i in range(len(self._node_pos)):
            if (i + 1) <= highest_unlocked and self._node_rect(i).collidepoint(pos):
                self._flash_node = i
                self._flash_time = pygame.time.get_ticks()
                return i + 1
        return None


# =============================================================================
# ENEMY  (Slime)
# =============================================================================

class Enemy(pygame.sprite.Sprite):
    MOVE_SPEED     = 1.5
    PATROL_RADIUS  = 1.5 * TILE_SIZE   # 1.5 tiles each side = 3 tiles total
    ANIM_SPEED     = 0.15
    GRAVITY        = 1
    MAX_FALL_SPEED = 10
    SCALE_FACTOR   = 1.5
    VISUAL_OFFSET_Y= 35
    WALK_FRAMES_AT_SPEED = int(PATROL_RADIUS / MOVE_SPEED)  # frames to cross one side

    # How long to idle at each end (frames)
    IDLE_DURATION  = 90   # ~1.5 seconds at 60fps

    def __init__(self, x: int, y: int):
        super().__init__()
        self.idle_frames = self._load_sheet("GRAPHICS/Enemies/Slime1.png", cols=6, row=2)
        self.walk_frames = self._load_sheet("GRAPHICS/Enemies/Slime2.png", cols=8, row=2)

        # Fixed anchor — patrol never drifts from spawn
        self.anchor_x  = float(x)
        self.pos_x     = float(x)
        self.vel_y     = 0
        self.on_ground = False

        # State: "WALK_LEFT" → "IDLE" → "WALK_RIGHT" → "IDLE" → repeat
        self.state     = "WALK_LEFT"
        self.direction = -1          # -1 = left, +1 = right
        self.idle_timer= 0
        self.current_frame = 0.0

        self.image  = self.walk_frames[0]
        self.rect   = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-60, -60)

    # ------------------------------------------------------------------
    def _load_sheet(self, path: str, cols: int, row: int) -> list[pygame.Surface]:
        sheet   = pygame.image.load(path).convert_alpha()
        frame_w = sheet.get_width()  // cols
        frame_h = sheet.get_height() // 4
        new_w   = int(frame_w * self.SCALE_FACTOR)
        new_h   = int(frame_h * self.SCALE_FACTOR)
        return [
            pygame.transform.scale(
                sheet.subsurface(pygame.Rect(i * frame_w, row * frame_h, frame_w, frame_h)),
                (new_w, new_h),
            )
            for i in range(cols)
        ]

    # ------------------------------------------------------------------
    def update(self, world) -> None:
        # ── State Machine ─────────────────────────────────────────────
        left_bound  = self.anchor_x - self.PATROL_RADIUS
        right_bound = self.anchor_x + self.PATROL_RADIUS

        if self.state == "WALK_LEFT":
            self.direction = -1
            self.pos_x    -= self.MOVE_SPEED
            if self.pos_x <= left_bound:
                self.pos_x  = left_bound   # clamp — no overshoot
                self.state  = "IDLE"
                self.idle_timer = 0

        elif self.state == "WALK_RIGHT":
            self.direction = 1
            self.pos_x    += self.MOVE_SPEED
            if self.pos_x >= right_bound:
                self.pos_x  = right_bound  # clamp
                self.state  = "IDLE"
                self.idle_timer = 0

        elif self.state == "IDLE":
            self.idle_timer += 1
            if self.idle_timer >= self.IDLE_DURATION:
                # Turn around: if we were going left, now go right — and vice versa
                self.state = "WALK_RIGHT" if self.direction == -1 else "WALK_LEFT"

        # ── Apply horizontal position ──────────────────────────────────
        self.rect.x = round(self.pos_x)

        # ── Wall collision (safety net) ────────────────────────────────
        for _, tile_rect in world.tile_list:
            if tile_rect.colliderect(self.rect):
                if self.direction == -1:
                    self.rect.left = tile_rect.right
                else:
                    self.rect.right = tile_rect.left
                self.pos_x = float(self.rect.x)
                # Flip state so it doesn't get stuck on a wall
                self.state = "WALK_RIGHT" if self.direction == -1 else "WALK_LEFT"
                break

        # ── Gravity ───────────────────────────────────────────────────
        self.vel_y     = min(self.vel_y + self.GRAVITY, self.MAX_FALL_SPEED)
        self.rect.y   += self.vel_y
        self.on_ground = False

        for _, tile_rect in world.tile_list:
            if tile_rect.colliderect(self.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile_rect.top
                    self.vel_y       = 0
                    self.on_ground   = True
                else:
                    self.rect.top = tile_rect.bottom
                    self.vel_y    = 0
                break

        # ── Hitbox ────────────────────────────────────────────────────
        self.hitbox.center = (self.rect.centerx, self.rect.centery + self.VISUAL_OFFSET_Y)

        # ── Animation ─────────────────────────────────────────────────
        is_walking = self.state in ("WALK_LEFT", "WALK_RIGHT")
        frames     = self.walk_frames if is_walking else self.idle_frames
        self.current_frame = (self.current_frame + self.ANIM_SPEED) % len(frames)
        raw_image  = frames[int(self.current_frame)]
        # Default sprite faces left; flip when going right
        self.image = pygame.transform.flip(raw_image, self.direction > 0, False)

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, (self.rect.x, self.rect.y + self.VISUAL_OFFSET_Y))


# =============================================================================
# PIXEL FONT
# =============================================================================

class PixelFont:
    CHAR_MAP = {
        'A':'1_01','B':'1_02','C':'1_03','D':'1_04','E':'1_05','F':'1_06',
        'G':'1_07','H':'1_08','I':'1_09','J':'1_10','K':'1_11','L':'1_12',
        'M':'1_13','N':'1_14','O':'1_15','P':'1_16','Q':'1_17','R':'1_18',
        'S':'1_19','T':'1_20','U':'1_21','V':'1_22','W':'1_23','X':'1_24',
        'Y':'1_25','Z':'1_26',
        '0':'1_27','1':'1_28','2':'1_29','3':'1_30','4':'1_31','5':'1_32',
        '6':'1_33','7':'1_34','8':'1_35','9':'1_36',
        '.':'1_37',':':'1_38',',':'1_39','+':'1_40','-':'1_41','=':'1_42',
        ';':'1_43',"'":'1_44','#':'1_45','|':'1_46','\\':'1_47','/':'1_48',
        '(':'1_49',')':'1_50','[':'1_51',']':'1_52','{':'1_53','}':'1_54',
        '!':'1_55','<':'1_56','>':'1_57','?':'1_58','%':'1_60',
    }
    LETTER_DIR = "GRAPHICS/UI/LETTERS/"

    def __init__(self, glyph_size: int = 24, spacing: int = 2):
        self.glyph_size = glyph_size
        self.spacing    = spacing
        self._cache: dict[str, pygame.Surface] = {}

    def _get_glyph(self, char: str) -> pygame.Surface | None:
        char = char.upper()
        if char not in self.CHAR_MAP:
            return None
        if char not in self._cache:
            path = self.LETTER_DIR + self.CHAR_MAP[char] + ".png"
            try:
                img = pygame.image.load(path).convert()
                img.set_colorkey((255, 255, 255))
                self._cache[char] = pygame.transform.scale(img, (self.glyph_size, self.glyph_size))
            except FileNotFoundError:
                return None
        return self._cache[char]

    def render(self, text: str, screen: pygame.Surface, x: int, y: int,color: tuple = None) -> int:
        cursor_x = x
        for char in text.upper():
            if char == ' ':
                cursor_x += self.glyph_size // 2 + self.spacing
                continue
            glyph = self._get_glyph(char)
            if glyph:
                if color:
                    # Create a transparent SRCALPHA surface
                    colored = pygame.Surface(
                        (self.glyph_size, self.glyph_size), pygame.SRCALPHA)
                    colored.fill((0, 0, 0, 0))          # fully transparent
                    colored.blit(glyph, (0, 0))          # blit black glyph (colorkey drops white)
                    colored.fill((*color, 0),             # add color to RGB, leave alpha alone
                    special_flags=pygame.BLEND_RGBA_ADD)
                    screen.blit(colored, (cursor_x, y))
                else:
                    screen.blit(glyph, (cursor_x, y))
                cursor_x += self.glyph_size + self.spacing
        return cursor_x - x

    def text_width(self, text: str) -> int:
        width = 0
        for char in text.upper():
            if char == ' ':
                width += self.glyph_size // 2 + self.spacing
            elif char in self.CHAR_MAP:
                width += self.glyph_size + self.spacing
        return width


# =============================================================================
# MENU BASE  — shared button logic for WinMenu and PauseMenu
# =============================================================================

class _ButtonMenu:
    """
    FIX 1: All buttons rendered at the same uniform width (widest label + padding).
            No more "floaty" mismatched boxes on every option.

    FIX 2: Clicking a button triggers a 150 ms bright flash — immediate tactile feedback.
    """

    CLICK_FLASH_MS = 150
    BTN_STEP       = 60
    BTN_PADDING    = 40   # horizontal padding added on each side of the widest label

    # Subclasses must define: OPTIONS, BTN_Y

    def __init__(self, glyph_size: int = 28):
        self.font = PixelFont(glyph_size)

        self._click_idx : int | None = None
        self._click_time: int        = 0

        # FIX 1: single shared width = widest label + padding
        self._btn_w = max(self.font.text_width(o) for o in self.OPTIONS) + self.BTN_PADDING * 2

    # ------------------------------------------------------------------
    def _button_rect(self, index: int) -> pygame.Rect:
        """Every button is the same width."""
        return pygame.Rect(
            SCREEN_WIDTH // 2 - self._btn_w // 2,
            self.BTN_Y + index * self.BTN_STEP,
            self._btn_w,
            self.font.glyph_size + 16,
        )

    # ------------------------------------------------------------------
    def _draw_buttons(
        self,
        screen     : pygame.Surface,
        mouse_pos  : tuple[int, int],
        hover_color: tuple,
        flash_color: tuple,
    ) -> None:
        now = pygame.time.get_ticks()

        for i, option in enumerate(self.OPTIONS):
            rect        = self._button_rect(i)
            is_hovered  = rect.collidepoint(mouse_pos)
            # FIX 2: flash takes visual priority over plain hover
            is_flashing = (
                i == self._click_idx
                and now - self._click_time < self.CLICK_FLASH_MS
            )

            if is_flashing:
                # Filled flash + coloured border
                flash_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                flash_surf.fill((*flash_color, 70))
                screen.blit(flash_surf, rect.topleft)
                pygame.draw.rect(screen, flash_color, rect, 4)
            elif is_hovered:
                pygame.draw.rect(screen, hover_color, rect, 4)

            # Centred label text
            tw = self.font.text_width(option)
            tx = SCREEN_WIDTH // 2 - tw // 2
            ty = rect.y + rect.height // 2 - self.font.glyph_size // 2
            self.font.render(option, screen, tx, ty)

    # ------------------------------------------------------------------
    def handle_click(self, pos: tuple[int, int]) -> int | None:
        for i in range(len(self.OPTIONS)):
            if self._button_rect(i).collidepoint(pos):
                # FIX 2: start the click flash
                self._click_idx  = i
                self._click_time = pygame.time.get_ticks()
                return i
        return None
# =============================================================================
# MENU BACKGROUND  — hacker/matrix vibe for the main menu
# =============================================================================

class MenuBackground:
    MATRIX_CHARS = "アイウエオカキクケコ0123456789ABCDEF<>{}[]|\\/#@!?01{}()"

    def __init__(self):
        self._mfont   = pygame.font.SysFont("courier", 16, bold=True)
        self._sfont   = pygame.font.SysFont("courier", 11, bold=False)

        # Two layers: fast green + slow dim layer
        col_count = SCREEN_WIDTH // 18
        self.rain_a = [
            {"x": i * 18,
             "y": random.randint(-SCREEN_HEIGHT, 0),
             "speed": random.randint(4, 9),
             "length": random.randint(10, 24)}
            for i in range(col_count)
        ]
        col_count2 = SCREEN_WIDTH // 30
        self.rain_b = [
            {"x": random.randint(0, SCREEN_WIDTH),
             "y": random.randint(-SCREEN_HEIGHT, 0),
             "speed": random.randint(1, 3),
             "length": random.randint(6, 14)}
            for i in range(col_count2)
        ]

        # Glitch
        self.glitch_active   = False
        self.glitch_timer    = 0
        self.glitch_cooldown = 0
        self.glitch_slices   = []

        # Scanlines (built once)
        self._scanlines = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for sy in range(0, SCREEN_HEIGHT, 3):
            pygame.draw.line(self._scanlines, (0, 0, 0, 60),
                             (0, sy), (SCREEN_WIDTH, sy))

        # Horizontal circuit lines
        self._circuit_y = [random.randint(50, SCREEN_HEIGHT - 50)
                           for _ in range(6)]
        self._circuit_x = [random.randint(0, SCREEN_WIDTH)
                           for _ in range(6)]

        # Floating binary blobs
        self._blobs = [
            {"x": random.randint(0, SCREEN_WIDTH),
             "y": random.randint(0, SCREEN_HEIGHT),
             "text": "".join(random.choice("01") for _ in range(random.randint(6, 14))),
             "alpha": random.randint(20, 60),
             "speed": random.uniform(0.2, 0.8)}
            for _ in range(18)
        ]

    # ------------------------------------------------------------------
    def _trigger_glitch(self):
        self.glitch_slices = [
            (random.randint(0, SCREEN_HEIGHT - 30),
             random.randint(2, 14),
             random.randint(-20, 20),
             random.choice([(0,255,100,25),(0,180,255,20),(255,255,0,15)]))
            for _ in range(random.randint(2, 4))
        ]
        self.glitch_active   = True
        self.glitch_timer    = random.randint(2, 6)
        self.glitch_cooldown = random.randint(90, 300)

    # ------------------------------------------------------------------
    def update(self):
        for col in self.rain_a:
            col["y"] += col["speed"]
            if col["y"] > SCREEN_HEIGHT + col["length"] * 18:
                col["y"]      = random.randint(-300, -20)
                col["speed"]  = random.randint(4, 9)
                col["length"] = random.randint(10, 24)

        for col in self.rain_b:
            col["y"] += col["speed"]
            if col["y"] > SCREEN_HEIGHT + col["length"] * 14:
                col["y"]      = random.randint(-200, -10)
                col["speed"]  = random.randint(1, 3)
                col["length"] = random.randint(6, 14)

        for blob in self._blobs:
            blob["y"] += blob["speed"]
            if blob["y"] > SCREEN_HEIGHT + 20:
                blob["y"]    = random.randint(-40, 0)
                blob["x"]    = random.randint(0, SCREEN_WIDTH)
                blob["text"] = "".join(random.choice("01") for _ in
                                       range(random.randint(6, 14)))

        if self.glitch_cooldown > 0:
            self.glitch_cooldown -= 1
        elif random.random() < 0.015:
            self._trigger_glitch()
        if self.glitch_active:
            self.glitch_timer -= 1
            if self.glitch_timer <= 0:
                self.glitch_active = False

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface):
        screen.fill((4, 8, 4))

        # ── Layer B — slow dim rain ───────────────────────────────────
        for col in self.rain_b:
            for i in range(col["length"]):
                cy = col["y"] - i * 14
                if cy < 0 or cy > SCREEN_HEIGHT:
                    continue
                ch   = random.choice(self.MATRIX_CHARS)
                dark = max(15, 45 - i * 4)
                surf = self._sfont.render(ch, True, (0, dark, 0))
                surf.set_alpha(80)
                screen.blit(surf, (col["x"], cy))

        # ── Layer A — fast bright rain ────────────────────────────────
        for col in self.rain_a:
            for i in range(col["length"]):
                cy = col["y"] - i * 18
                if cy < 0 or cy > SCREEN_HEIGHT:
                    continue
                ch = random.choice(self.MATRIX_CHARS)
                if i == 0:
                    color = (180, 255, 180)
                elif i < 3:
                    color = (0, 210, 70)
                else:
                    color = (0, max(20, 100 - i * 6), 0)
                screen.blit(self._mfont.render(ch, True, color), (col["x"], cy))

        # ── Floating binary blobs ─────────────────────────────────────
        for blob in self._blobs:
            surf = self._sfont.render(blob["text"], True, (0, 160, 40))
            surf.set_alpha(blob["alpha"])
            screen.blit(surf, (blob["x"], blob["y"]))

        # ── Horizontal circuit traces ─────────────────────────────────
        now = pygame.time.get_ticks()
        for i, cy in enumerate(self._circuit_y):
            pulse = abs(((now // 12 + i * 120) % 400) - 200) / 200
            alpha = int(20 + pulse * 35)
            lsurf = pygame.Surface((SCREEN_WIDTH, 1), pygame.SRCALPHA)
            lsurf.fill((0, 200, 60, alpha))
            screen.blit(lsurf, (0, cy))
            # Node dots along the line
            for nx in range(0, SCREEN_WIDTH, 80):
                dot_a = int(30 + pulse * 60)
                pygame.draw.circle(screen, (0, 200, 60, dot_a),
                                   (nx + (i * 23) % 80, cy), 2)

        # ── Dark vignette overlay ─────────────────────────────────────
        vign = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        vign.fill((0, 0, 0, 0))
        for vy in range(0, SCREEN_HEIGHT // 3):
            a = int(110 * (1 - vy / (SCREEN_HEIGHT // 3)))
            pygame.draw.line(vign, (0, 0, 0, a), (0, vy), (SCREEN_WIDTH, vy))
        for vy in range(SCREEN_HEIGHT * 2 // 3, SCREEN_HEIGHT):
            a = int(110 * (vy - SCREEN_HEIGHT * 2 // 3) / (SCREEN_HEIGHT // 3))
            pygame.draw.line(vign, (0, 0, 0, a), (0, vy), (SCREEN_WIDTH, vy))
        screen.blit(vign, (0, 0))

        # ── Glitch slices ─────────────────────────────────────────────
        if self.glitch_active:
            for (gy, gh, goff, gcol) in self.glitch_slices:
                band = pygame.Surface((SCREEN_WIDTH, gh), pygame.SRCALPHA)
                band.fill(gcol)
                screen.blit(band, (0, gy))
                safe_w = SCREEN_WIDTH - abs(goff)
                if safe_w > 0 and gh > 0:
                    try:
                        sl = screen.subsurface(
                            pygame.Rect(0, gy, safe_w, gh)).copy()
                        screen.blit(sl, (goff, gy))
                    except ValueError:
                        pass

        # ── Scanlines ────────────────────────────────────────────────
        screen.blit(self._scanlines, (0, 0))

# =============================================================================
# MENU  (Language Selection)
# =============================================================================

class Menu:
    """
    FIX 1: Uniform button widths — all language buttons share the same width.
    FIX 2: Click flash feedback on selection.
    """

    LANGUAGES   = ["Python", "Java", "JavaScript", "HTML", "CSS"]
    BTN_Y_START = 480
    BTN_STEP    = 70
    GLYPH_SIZE  = 28
    TITLE_GLYPH = 36
    BTN_PADDING = 40
    FLASH_MS    = 150

    def __init__(self):
        self.font       = PixelFont(self.GLYPH_SIZE)
        self.title_font = PixelFont(self.TITLE_GLYPH)
        self.hovered    = -1
        self.logo       = self._load_logo()
        self.arrow      = self._load_arrow()

        # FIX 1: one shared width for all language buttons
        self._btn_w      = max(self.font.text_width(l) for l in self.LANGUAGES) + self.BTN_PADDING * 2
        self._click_idx  : int | None = None
        self._click_time : int        = 0

    def _load_logo(self) -> pygame.Surface | None:
        try:
            return pygame.transform.scale(
                pygame.image.load("GRAPHICS/UI/Logo.png").convert_alpha(), (700, 120)
            )
        except FileNotFoundError:
            return None

    def _load_arrow(self) -> pygame.Surface | None:
        try:
            return pygame.transform.scale(
                pygame.image.load("GRAPHICS/UI/Arrow.png").convert_alpha(), (36, 36)
            )
        except FileNotFoundError:
            return None

    def _button_rect(self, index: int) -> pygame.Rect:
        # FIX 1: uniform width
        return pygame.Rect(
            SCREEN_WIDTH // 2 - self._btn_w // 2,
            self.BTN_Y_START + index * self.BTN_STEP,
            self._btn_w,
            self.GLYPH_SIZE + 16,
        )

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int],
            bg: "MenuBackground" = None) -> None:
        if bg:
            bg.draw(screen)
        else:
            screen.fill(DARK)

        # Title
        title_text = "THE SYNTAX ESCAPE"
        if self.logo:
            logo_x = SCREEN_WIDTH // 2 - self.logo.get_width() // 2
            logo_y = 80
            screen.blit(self.logo, (logo_x, logo_y))
            tw = self.title_font.text_width(title_text)
            tx = SCREEN_WIDTH // 2 - tw // 2
            ty = logo_y + self.logo.get_height() // 2 - self.TITLE_GLYPH // 2 - 16
            self.title_font.render(title_text, screen, tx, ty)
        else:
            tw = self.title_font.text_width(title_text)
            self.title_font.render(title_text, screen, SCREEN_WIDTH // 2 - tw // 2, 100, color=WHITE)

        sub = "SELECT LANGUAGE"
        sw  = self.font.text_width(sub)
        self.font.render(sub, screen, SCREEN_WIDTH // 2 - sw // 2, 390, color=WHITE)

        # Detect hovered button
        self.hovered = -1
        for i in range(len(self.LANGUAGES)):
            if self._button_rect(i).collidepoint(mouse_pos):
                self.hovered = i

        now = pygame.time.get_ticks()

        for i, lang in enumerate(self.LANGUAGES):
            rect        = self._button_rect(i)
            is_hovered  = (i == self.hovered)
            # FIX 2: flash after click
            is_flashing = (i == self._click_idx and now - self._click_time < self.FLASH_MS)

            if is_flashing:
                flash_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                flash_surf.fill((255, 215, 0, 80))
                screen.blit(flash_surf, rect.topleft)
                pygame.draw.rect(screen, GOLD, rect, 4)
            elif is_hovered:
                highlight = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 25))
                screen.blit(highlight, rect.topleft)

            lw = self.font.text_width(lang)
            lx = SCREEN_WIDTH // 2 - lw // 2
            ly = rect.y + rect.height // 2 - self.GLYPH_SIZE // 2

            if is_hovered and self.arrow:
                ax = rect.left + 8
                ay = ly + self.GLYPH_SIZE // 2 - self.arrow.get_height() // 2
                screen.blit(self.arrow, (ax, ay))

            if is_hovered or is_flashing:
                # Gold tint on hover / flash
                tmp  = pygame.Surface((lw, self.GLYPH_SIZE), pygame.SRCALPHA)
                self.font.render(lang, tmp, 0, 0)
                tint = pygame.Surface((lw, self.GLYPH_SIZE), pygame.SRCALPHA)
                tint.fill((255, 215, 0, 120))
                tmp.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(tmp, (lx, ly))
            else:
                self.font.render(lang, screen, lx, ly, color=WHITE)

        # Custom arrow cursor
        if self.arrow:
            screen.blit(self.arrow, mouse_pos)

    def handle_click(self, pos: tuple[int, int]) -> str | None:
        for i, lang in enumerate(self.LANGUAGES):
            if self._button_rect(i).collidepoint(pos):
                # FIX 2: start flash
                self._click_idx  = i
                self._click_time = pygame.time.get_ticks()
                return lang
        return None


# =============================================================================
# WIN MENU
# =============================================================================
class WinMenu(_ButtonMenu):
    OPTIONS    = ["NEXT LEVEL", "WORLD MAP", "MAIN MENU"]
    ICON_FILES = ["NEXT_ICON.png", "MAP_ICON.png", "MAINMENU_ICON.png"]
    BTN_Y      = 450
    BTN_STEP   = 60
    PANEL_W    = 580
    PANEL_H    = 340
    ICON_SIZE  = (56, 56)
    SLOT_W     = 100
    SLOT_H     = 100
    SLOT_DY    = 175
    SLOT_DX    = 40
    ICON_COLORS = [GOLD, CYAN, NEON_GREEN]
    
    # Flash and hover effect settings
    FLASH_DURATION = 300  # ms
    HOVER_SCALE = 1.15
    HOVER_BRIGHTNESS = 40  # Pure Pygame brightness boost
    FLASH_BRIGHTNESS = 60

    def __init__(self):
        super().__init__(glyph_size=20)
        self._bg    = self._load_img("GRAPHICS/UI/WIN_SETTINGS.png", (self.PANEL_W, self.PANEL_H))
        self._icons = [self._load_icon(f"GRAPHICS/UI/ICONS/{f}", self.ICON_SIZE) for f in self.ICON_FILES]
        self._small_font = PixelFont(12)
        
        # State tracking for effects
        self._hover_idx = None
        self._flash_idx = None
        self._flash_start_time = 0

    def _load_img(self, path, size):
        try:
            surf = pygame.transform.scale(
                pygame.image.load(path).convert_alpha(), size)
            surf.set_colorkey((255, 255, 255))
            return surf
        except FileNotFoundError:
            return None

    def _load_icon(self, path, size):
        try:
            return pygame.transform.scale(
                pygame.image.load(path).convert_alpha(), size)
        except FileNotFoundError:
            return None

    def _panel_topleft(self):
        return (SCREEN_WIDTH  // 2 - self.PANEL_W // 2 ,
                SCREEN_HEIGHT // 2 - self.PANEL_H // 2)

    def _slot_rect(self, index):
        px, py  = self._panel_topleft()
        spacing = (self.PANEL_W - 3 * self.SLOT_W ) // 4 # even 4-gap distribution
        sx = px + spacing + index * (self.SLOT_W + spacing - 40 ) + self.SLOT_DX
        sy = py + self.SLOT_DY
        return pygame.Rect(sx, sy, self.SLOT_W, self.SLOT_H)

    def update(self, mouse_pos):
        """Call this every frame to update hover/flash states"""
        self._hover_idx = None
        for i in range(len(self.OPTIONS)):
            if self._slot_rect(i).collidepoint(mouse_pos):
                self._hover_idx = i
                break
        
        # Update flash state
        if self._flash_idx is not None:
            if pygame.time.get_ticks() - self._flash_start_time > self.FLASH_DURATION:
                self._flash_idx = None

    def _brighten_surface(self, surface, brightness):
        """NEW: Pure Pygame brightness boost (no numpy!)"""
        bright_surf = surface.copy()
        arr = pygame.surfarray.pixels3d(bright_surf)
        del arr
        pygame.surfarray.blit_array(bright_surf, arr)  # No, wrong!
        return bright_surf
        
        
    def draw(self, screen, mouse_pos):
        # Update states before drawing
        self.update(mouse_pos)
        
        px, py = self._panel_topleft()
        if self._bg:
            screen.blit(self._bg, (px, py))

        SLOT_LABELS = ["NEXT", "MAP", "MENU"]

        for i, label in enumerate(SLOT_LABELS):
            rect = self._slot_rect(i)
            is_hovered  = (i == self._hover_idx)
            is_flashing = (i == self._flash_idx)

            # Glow — blit at rect.x/y not centerx
            if is_hovered or is_flashing:
                glow_color = list(self.ICON_COLORS[i])
                if is_flashing:
                    flash_progress = (pygame.time.get_ticks() - self._flash_start_time) / self.FLASH_DURATION
                    pulse = int(50 * (1 - flash_progress))
                    glow_color = tuple(min(255, c + pulse) for c in glow_color)
                glow_surf = pygame.Surface((rect.width + 24, rect.height + 24), pygame.SRCALPHA)
                pygame.draw.ellipse(glow_surf, (*glow_color, 80 if is_hovered else 120),
                                    (0, 0, rect.width + 24, rect.height + 24))
                screen.blit(glow_surf, (rect.x - 12, rect.y - 12))  # ← was rect.centerx

            # Label — centred above slot using rect.centerx
            lw = self._small_font.text_width(label)
            text_x = rect.centerx - lw // 2                 
            text_y = rect.top - 22
            self._small_font.render(label, screen, text_x, text_y)

            # Icon — centred inside slot
            if self._icons[i]:
                ico = self._icons[i]
                scale = 1.0
                brightness = 0
                if is_hovered:
                    scale = self.HOVER_SCALE
                    brightness = self.HOVER_BRIGHTNESS
                elif is_flashing:
                    flash_progress = (pygame.time.get_ticks() - self._flash_start_time) / self.FLASH_DURATION
                    scale = self.HOVER_SCALE * (1.1 - 0.1 * flash_progress)
                    brightness = int(self.FLASH_BRIGHTNESS * (1 - flash_progress))

                padding = 12 if is_hovered or is_flashing else 20
                max_w = rect.width  - padding
                max_h = rect.height - padding
                new_w = min(int(ico.get_width()  * scale), max_w)
                new_h = min(int(ico.get_height() * scale), max_h)
                scaled_ico = pygame.transform.smoothscale(ico, (new_w, new_h))

                if brightness > 0:
                    bright_ico = scaled_ico.copy()
                    bright_ico.fill((brightness, brightness, brightness),
                                    special_flags=pygame.BLEND_ADD)
                    scaled_ico = bright_ico

                ico_x = rect.centerx - scaled_ico.get_width()  // 2 
                ico_y = rect.centery - scaled_ico.get_height() // 2
                screen.blit(scaled_ico, (ico_x, ico_y))

    def handle_click(self, pos):
        for i in range(len(self.OPTIONS)):
            if self._slot_rect(i).collidepoint(pos):
                # Trigger flash effect
                self._flash_idx = i
                self._flash_start_time = pygame.time.get_ticks()
                self._click_idx = i
                self._click_time = pygame.time.get_ticks()
                return i
        return None


# =============================================================================
# GAME OVER SCREEN
# =============================================================================

class GameOverScreen:
    PANEL_W        = 580
    PANEL_H        = 340
    HEADER_H       = 50
    SLOT_W         = 108
    SLOT_H         = 108
    SLOT_DY        = 165
    SLOT_DX        = 40
    ICON_SIZE      = (56, 56)
    CLICK_FLASH_MS = 150

    def __init__(self):
        self.font        = PixelFont(22)
        self.small_font  = PixelFont(16)
        self._bg         = self._load_img("GRAPHICS/UI/GAMEOVER.png",         (self.PANEL_W, self.PANEL_H))
        self._map_ico    = self._load_icon("GRAPHICS/UI/ICONS/MAP_ICON.png",   self.ICON_SIZE)
        self._retry_ico  = self._load_icon("GRAPHICS/UI/ICONS/RESTART_ICON.png",  self.ICON_SIZE)
        self._menu_ico   = self._load_icon("GRAPHICS/UI/ICONS/MAINMENU_ICON.png", self.ICON_SIZE)
        # Public stats – updated by main() each frame before draw()
        self.elapsed_secs : int       = 0
        self.deaths       : int       = 0
        self.score        : int       = 0
        self._click_idx   : int|None  = None
        self._click_time  : int       = 0

    # ------------------------------------------------------------------
    def _load_img(self, path: str, size: tuple) -> pygame.Surface | None:
        """For panel backgrounds — strips white background."""
        try:
            surf = pygame.transform.scale(
                pygame.image.load(path).convert_alpha(), size)
            surf.set_colorkey((255, 255, 255))
            return surf
        except FileNotFoundError:
            return None

    def _load_icon(self, path: str, size: tuple) -> pygame.Surface | None:
        """For icons — preserves all pixels including white."""
        try:
            return pygame.transform.scale(
                pygame.image.load(path).convert_alpha(), size)
        except FileNotFoundError:
            return None

    def _panel_topleft(self) -> tuple[int, int]:
        return (SCREEN_WIDTH  // 2 - self.PANEL_W // 2,
                SCREEN_HEIGHT // 2 - self.PANEL_H // 2)

    def _slot_rect(self, index: int) -> pygame.Rect:
        px, py  = self._panel_topleft()
        spacing = (self.PANEL_W - 3 * self.SLOT_W) // 4
        sx = px + spacing + index * (self.SLOT_W + spacing - 40) + self.SLOT_DX
        sy = py + self.SLOT_DY
        return pygame.Rect(sx, sy, self.SLOT_W, self.SLOT_H)

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int] = (0, 0)) -> None:
        px, py = self._panel_topleft()

        # Dark veil so the game world recedes
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 160))
        screen.blit(veil, (0, 0))

        # Panel background
        if self._bg:
            screen.blit(self._bg, (px, py))
        else:
            pygame.draw.rect(screen, (15, 15, 40), (px, py, self.PANEL_W, self.PANEL_H))
            pygame.draw.rect(screen, (60, 60, 120), (px, py, self.PANEL_W, self.PANEL_H), 2)

        # "GAME OVER" — perfectly centred in the full header bar
        title = "GAME OVER"
        tw    = self.font.text_width(title)
        ty    = py + (self.HEADER_H - self.font.glyph_size) // 2
        self.font.render(title, screen, px + self.PANEL_W // 2 - tw // 2, ty)

        # Separator line beneath the header bar
        pygame.draw.line(screen, (80, 80, 140),(px + 4,py + self.HEADER_H),(px + self.PANEL_W - 4, py + self.HEADER_H), 2)

        # --- Three slots: RETRY | DEATHS | MAIN MENU ---
        SLOT_DATA = [
        ("RETRY",     self._retry_ico, True),
        ("MAP",       self._map_ico,   True),
        ("MAIN",      self._menu_ico,  True),
        ]

        now = pygame.time.get_ticks()

        for i, (label, icon, clickable) in enumerate(SLOT_DATA):
            rect = self._slot_rect(i)

            # Label above the slot
            lw = self.small_font.text_width(label)
            self.small_font.render(label, screen,rect.centerx - lw // 2,rect.top - 22)

            # Hover / flash only on clickable slots
            if clickable:
                is_hovered  = rect.collidepoint(mouse_pos)
                is_flashing = (i == self._click_idx and now - self._click_time < self.CLICK_FLASH_MS)
                if is_flashing:
                    glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    glow.fill((255, 215, 0, 90))
                    screen.blit(glow, rect.topleft)
                    pygame.draw.rect(screen, WHITE, rect, 3)
                elif is_hovered:
                    glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    glow.fill((255, 255, 255, 40))
                    screen.blit(glow, rect.topleft)
                    pygame.draw.rect(screen, GOLD, rect, 3)

            # Draw icon centred inside the square slot (no circles)
            if icon:
                ix = rect.centerx - icon.get_width()  // 2
                iy = rect.centery - icon.get_height() // 2
                screen.blit(icon, (ix, iy))
            elif i == 1:
                # Fallback: draw deaths number if no icon loaded
                val = str(self.deaths)
                vw  = self.font.text_width(val)
                self.font.render(val, screen,
                                 rect.centerx - vw // 2,
                                 rect.centery - self.font.glyph_size // 2)

    # ------------------------------------------------------------------
    def handle_click(self, pos: tuple[int, int]) -> int | None:
        """Returns 0 = RETRY, 2 = MAIN MENU, None = nothing hit."""
        for i, clickable in enumerate([True, True, True]):
            if clickable and self._slot_rect(i).collidepoint(pos):
                self._click_idx  = i
                self._click_time = pygame.time.get_ticks()
                return i
        return None


# =============================================================================
# PAUSE MENU
# =============================================================================

class PauseMenu(_ButtonMenu):
    OPTIONS  = ["CONTINUE", "MAIN MENU", "RESET"]
    BTN_Y    = 400
    BTN_STEP = 60
    PANEL_W  = 420
    PANEL_H  = 520
    ROW_H    = 93
    ROW_Y0   = 55
    BTN_H    = 60

    def __init__(self):
        super().__init__(glyph_size=24)
        self._bg         = self._load_img("GRAPHICS/UI/SETTINGS.png", (self.PANEL_W, self.PANEL_H))
        self._set_ico    = self._load_img("GRAPHICS/UI/ICONS/SETTINGS_ICON.png", (28, 28))
        self._exit_ico   = self._load_img("GRAPHICS/UI/ICONS/EXIT_ICON.png", (28, 28))
        self._vol_on_ico = self._load_img("GRAPHICS/UI/ICONS/VOLUMEON_ICON.png", (36, 36))
        self._vol_off_ico= self._load_img("GRAPHICS/UI/ICONS/VOLUMEOFF_ICON.png", (36, 36))
        self._map_ico    = self._load_img("GRAPHICS/UI/ICONS/MAP_ICON.png", (36, 36))
        self.volume_on   = True
        

    def _load_img(self, path: str, size: tuple) -> pygame.Surface | None:
        try:
            return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
        except FileNotFoundError:
            return None

    def _panel_topleft(self) -> tuple[int, int]:
        return (SCREEN_WIDTH // 2 - self.PANEL_W // 2, SCREEN_HEIGHT // 2 - self.PANEL_H // 2)

    def _row_rect(self, index: int) -> pygame.Rect:
        px, py = self._panel_topleft()
        row_top = py + self.ROW_Y0 + index * self.ROW_H
        btn_top = row_top + (self.ROW_H - self.BTN_H) // 2
        return pygame.Rect(px + 25, btn_top, self.PANEL_W - 50, self.BTN_H)

    def _settings_rect(self) -> pygame.Rect:
        px, py = self._panel_topleft()
        return pygame.Rect(px + 10, py + (self.ROW_Y0 - 28) // 2, 28, 28)

    def _exit_rect(self) -> pygame.Rect:
        px, py = self._panel_topleft()
        # Perfectly centred vertically in the header, flush to right with 8px margin
        return pygame.Rect(px + self.PANEL_W - 36, py + (self.ROW_Y0 - 28) // 2, 28, 28)

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        # Dark veil
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 210))
        screen.blit(veil, (0, 0))

        px, py = self._panel_topleft()
        if self._bg:
            screen.blit(self._bg, (px, py))

        now = pygame.time.get_ticks()

        # "PAUSED" perfectly centered
        label = "PAUSED"
        lw = self.font.text_width(label)
        self.font.render(label, screen, SCREEN_WIDTH // 2 - lw // 2, py + (self.ROW_Y0 - self.font.glyph_size) // 2 + 5)

        # Exit X
        exit_rect = self._exit_rect()
        exit_hovered = exit_rect.collidepoint(mouse_pos)
        if self._exit_ico:
            if exit_hovered:
                tinted = self._exit_ico.copy()
                tinted.fill((255, 100, 100, 100), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(tinted, exit_rect.topleft)
                pygame.draw.rect(screen, (255, 50, 50), exit_rect, 2)
            else:
                screen.blit(self._exit_ico, exit_rect.topleft)
        else:
            pygame.draw.line(screen, WHITE, exit_rect.topleft, exit_rect.bottomright, 3)
            pygame.draw.line(screen, WHITE, exit_rect.topright, exit_rect.bottomleft, 3)

        # Separator
        sep_y = py + self.ROW_Y0 - 2
        pygame.draw.line(screen, (100, 100, 180), (px + 8, sep_y), (px + self.PANEL_W - 8, sep_y), 2)

        # === 3 ACTION BUTTONS ===
        for i, option in enumerate(self.OPTIONS):
            rect = self._row_rect(i)
            is_hovered = rect.collidepoint(mouse_pos)
            is_flashing = (i == self._click_idx and now - self._click_time < self.CLICK_FLASH_MS)

            if is_flashing:
                flash_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                flash_surf.fill((255, 255, 255, 70))
                screen.blit(flash_surf, rect.topleft)
                pygame.draw.rect(screen, WHITE, rect, 3)
            elif is_hovered:
                pygame.draw.rect(screen, GREEN, rect, 3)

            # PERFECT CENTER TEXT
            tw = self.font.text_width(option)
            tx = SCREEN_WIDTH // 2 - tw // 2
            base_ty = rect.centery - self.font.glyph_size // 2
            if i == 0:              # CONTINUE
                ty = base_ty + 16   # Lower 4px (change -4 to +4 to raise)
            elif i == 1:            # MAIN MENU (optional)
                ty = base_ty + 10    # Raise 2px (optional)
            else:                   # RESET
                ty = base_ty + 4     # No change
            self.font.render(option, screen, tx, ty)

        # === VOLUME ROW ===
        vol_rect = self._row_rect(3)
        vol_hovered = vol_rect.collidepoint(mouse_pos)
        vol_ico = self._vol_on_ico if self.volume_on else self._vol_off_ico
        vol_label = "SOUND ON" if self.volume_on else "SOUND OFF"
        map_rect    = self._row_rect(4)
        map_hovered = map_rect.collidepoint(mouse_pos)


        if vol_hovered:
            col = NEON_GREEN if self.volume_on else (200, 60, 60)
            pygame.draw.rect(screen, col, vol_rect, 3)

        if vol_ico:
            ix = vol_rect.x + 55
            iy = vol_rect.centery - vol_ico.get_height() // 2 - 5
            screen.blit(vol_ico, (ix, iy))
            lx = ix + vol_ico.get_width() + 5
            ly = vol_rect.centery - self.font.glyph_size // 2 - 4
            self.font.render(vol_label, screen, lx, ly)
            
        if map_hovered:
            pygame.draw.rect(screen, CYAN, map_rect, 3)
            
        if self._map_ico:
            ix = map_rect.x + 55
            iy = map_rect.centery - self._map_ico.get_height() // 2 - 5
            screen.blit(self._map_ico, (ix, iy))
            lx = ix + self._map_ico.get_width() + 5
            ly = map_rect.centery - self.font.glyph_size // 2 - 4
            self.font.render("WORLD MAP", screen, lx, ly)


    def handle_click(self, pos: tuple[int, int]) -> int | None:
        # World map row  ← ADD AT THE TOP
        if self._row_rect(4).collidepoint(pos):
            return 4

        # Exit X = close menu
        if self._exit_rect().collidepoint(pos):
            return 0  # CONTINUE (close menu)

        # Volume toggle
        if self._row_rect(3).collidepoint(pos):
            self.volume_on = not self.volume_on
            if self.volume_on:
                pygame.mixer.music.set_volume(0.5)
                # If music was stopped, you might need to play it again
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.set_volume(0.0)
            return None

        # Action buttons
        for i in range(len(self.OPTIONS)):
            if self._row_rect(i).collidepoint(pos):
                self._click_idx = i
                self._click_time = pygame.time.get_ticks()
                return i
        return None
# =============================================================================
# PARTICLE SYSTEM  ✨
# =============================================================================

class Particle(pygame.sprite.Sprite):
    """Individual particle with physics, color fade, and gravity."""
    
    def __init__(self, x: float, y: float, vel_x: float, vel_y: float, color: tuple, lifetime: int, size: int = 4):
        super().__init__()
        self.pos_x   = x
        self.pos_y   = y
        self.vel_x   = vel_x
        self.vel_y   = vel_y
        self.color   = list(color)
        self.lifetime = lifetime
        self.age     = 0
        self.size    = size
        self.gravity = 0.15
        self.friction = 0.98
        
        # Initial size variation
        self.max_size = size + 2
        self.image = self._create_image()
        self.rect  = self.image.get_rect(center=(round(x), round(y)))
    
    def _create_image(self) -> pygame.Surface:
        surf = pygame.Surface((self.max_size, self.max_size), pygame.SRCALPHA)
        alpha = max(50, 255 * (1 - self.age / self.lifetime))
        pygame.draw.circle(surf, (*self.color, int(alpha)),(self.max_size//2, self.max_size//2), self.size)
        return surf
    
    def update(self):
        self.age += 1
        if self.age > self.lifetime:
            self.kill()
            return
        
        # Physics
        self.vel_y += self.gravity
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        
        # Fade color
        fade = self.age / self.lifetime
        self.color[0] = int(self.color[0] * (1 - fade * 0.5))
        self.color[1] = int(self.color[1] * (1 - fade * 0.5))
        self.color[2] = int(self.color[2] * (1 - fade * 0.5))
        
        # Shrink
        self.size = max(1, self.max_size - int(fade * self.max_size))
        
        # Update visual
        self.image = self._create_image()
        self.rect.center = (round(self.pos_x), round(self.pos_y))

class ParticleManager:
    """Manages particle pools for performance."""
    
    def __init__(self, max_particles: int = 300):
        self.particles = pygame.sprite.Group()
        self.max_particles = max_particles
        self.pool = []
        self.next_id = 0
    
    def emit(self, x: float, y: float, count: int = 8, **kwargs):
        """Spawn particles at position with random variation."""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
                
            # Random variation
            vel_spread = kwargs.get('vel_spread', 4)
            vel_x = (self.next_id * 0.3) % vel_spread - vel_spread/2
            vel_y = -(self.next_id * 0.2) % (vel_spread * 0.7)
            
            color = kwargs.get('color', (255, 255, 100))
            lifetime = kwargs.get('lifetime', 40)
            size = kwargs.get('size', 4)
            
            particle = Particle(x, y, vel_x, vel_y, color, lifetime, size)
            self.particles.add(particle)
            self.next_id += 1
    
    def emit_land(self, x: float, y: float):
        """Landing dust effect."""
        self.emit(x, y, count=6, vel_spread=2, color=(200, 180, 120), lifetime=30, size=3)
    
    def emit_jump(self, x: float, y: float):
        """Jump puff."""
        self.emit(x, y, count=5, vel_spread=3, color=(120, 180, 255), lifetime=25, size=2)
    
    def emit_death(self, x: float, y: float):
        """Player death explosion."""
        for i in range(20):
            angle = i * 0.3
            vel_x = 6 * pygame.math.Vector2(1, 0).rotate(angle*180/3.14).x
            vel_y = 6 * pygame.math.Vector2(1, 0).rotate(angle*180/3.14).y
            color = [(255, 100, 100), (255, 150, 100), (255, 255, 100)][i%3]
            p = Particle(x, y, vel_x, vel_y, color, 60, 6)
            self.particles.add(p)
    
    def emit_slime(self, x: float, y: float):
        """Slime squish effect."""
        self.emit(x, y+20, count=12, vel_spread=3, color=(100, 255, 150), lifetime=35, size=3)
    
    def emit_gate(self, x: float, y: float):
        """Gate opening sparkles."""
        self.emit(x+40, y+20, count=15, vel_spread=2, color=(0, 255, 255), lifetime=45, size=2)
    
    def update(self):
        self.particles.update()
    
    def draw(self, screen: pygame.Surface):
        self.particles.draw(screen)

# =============================================================================
# GAME HELPERS
# =============================================================================

def spawn_slimes(slime_group: pygame.sprite.Group, world_data) -> None:
    """Spawn slimes based on current world data."""
    slime_group.empty()
    spawn_positions = get_slime_spawn_positions(world_data)
    for x, y in spawn_positions:
        slime_group.add(Enemy(x, y))
        
def reset_game(player: Player, slime_group: pygame.sprite.Group, world, world_data) -> None:
    player.rect.x           = -5
    player.rect.y           = SCREEN_HEIGHT - 350
    player.hitbox.center    = player.rect.center
    
    # FIX: Reset the hitbox tracking coordinates correctly
    player.pos_x            = float(player.hitbox.x)
    player.pos_y            = float(player.hitbox.y)
    
    player.vel_x            = 0.0
    player.vel_y            = 0.0
    player.jumped           = False
    player.on_ground        = False
    player.is_dying         = False
    player.is_playing_idle  = False
    player.status           = "STAND"
    player.frame_index      = 0.0
    player.respawn_time     = pygame.time.get_ticks()
    player.last_action_time = pygame.time.get_ticks()
    player.quiz_trigger_slime = None
    spawn_slimes(slime_group, world_data)
    for gate in world.gate_group:
        gate.reset()

def full_reset_game(player: Player, slime_group: pygame.sprite.Group,world, world_data) -> None:
    """Full reset — also resets HP. Use on retry/main menu."""
    reset_game(player, slime_group, world, world_data)
    player.hp = MAX_HP

# =============================================================================
# QUIZ POPUP  — terminal-style syntax challenge
# =============================================================================

class QuizPopup:
    PANEL_W  = 720
    PANEL_H  = 420
    FLASH_MS = 800   # how long correct/wrong feedback shows

    OPTION_LABELS = ["A", "B", "C", "D"]
    TERM_COLOR    = (0, 255, 100)      # matrix green
    WRONG_COLOR   = (255, 60,  60)
    RIGHT_COLOR   = (0,  255, 100)
    BG_COLOR      = (5,  12,  5)
    BORDER_COLOR  = (0,  180, 60)

    def __init__(self, language: str):
        self.language  = language
        self.questions = QUIZ_QUESTIONS.get(language, []).copy()
        random.shuffle(self.questions)
        self._q_index  = 0
        self._current  = self.questions[0] if self.questions else None

        self._sysfont  = pygame.font.SysFont("courier", 18, bold=True)
        self._qtfont   = pygame.font.SysFont("courier", 17, bold=True)
        self._smfont   = pygame.font.SysFont("courier", 15, bold=True)

        # Feedback state
        self._feedback      = None   # None | "correct" | "wrong"
        self._feedback_time = 0
        self._blink         = True
        self._blink_timer   = 0

        # Click flash per option
        self._click_opt  = None
        self._click_time = 0

        self.result      = None  # set to "correct" / "wrong" after feedback shown
        self.done        = False

    # ------------------------------------------------------------------
    def _panel_rect(self):
        return pygame.Rect(
            SCREEN_WIDTH  // 2 - self.PANEL_W // 2,
            SCREEN_HEIGHT // 2 - self.PANEL_H // 2,
            self.PANEL_W, self.PANEL_H)

    def _option_rect(self, i):
        pr = self._panel_rect()
        w  = (self.PANEL_W - 60) // 2
        h  = 52
        col = i % 2
        row = i // 2
        x = pr.x + 20 + col * (w + 20)
        y = pr.y + 220 + row * (h + 12)
        return pygame.Rect(x, y, w, h)

    # ------------------------------------------------------------------
    def handle_click(self, pos):
        if self._feedback is not None:
            return
        if self._current is None:
            return
        for i in range(4):
            if self._option_rect(i).collidepoint(pos):
                self._click_opt  = i
                self._click_time = pygame.time.get_ticks()
                if i == self._current["answer"]:
                    self._feedback      = "correct"
                else:
                    self._feedback      = "wrong"
                self._feedback_time = pygame.time.get_ticks()
                break

    # ------------------------------------------------------------------
    def update(self):
        now = pygame.time.get_ticks()

        # Blink cursor
        self._blink_timer += 1
        if self._blink_timer > 20:
            self._blink       = not self._blink
            self._blink_timer = 0

        # Check if feedback period is over → signal done
        if self._feedback is not None:
            if now - self._feedback_time > self.FLASH_MS:
                self.result = self._feedback
                self.done   = True

    # ------------------------------------------------------------------
    def _wrap_text(self, font, text, max_w):
        """Simple word-wrap returning list of strings."""
        words  = text.split()
        lines  = []
        line   = ""
        for w in words:
            test = line + (" " if line else "") + w
            if font.size(test)[0] <= max_w:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface, mouse_pos: tuple):
        if self._current is None:
            return

        now = pygame.time.get_ticks()
        pr  = self._panel_rect()

        # ── Veil ─────────────────────────────────────────────────────
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 190))
        screen.blit(veil, (0, 0))

        # ── Panel background ─────────────────────────────────────────
        pygame.draw.rect(screen, self.BG_COLOR,    pr)
        pygame.draw.rect(screen, self.BORDER_COLOR, pr, 3)

        # ── Scanlines ────────────────────────────────────────────────
        for sy in range(pr.y, pr.y + pr.h, 4):
            pygame.draw.line(screen, (0, 30, 0),(pr.x, sy), (pr.x + pr.w, sy))

        # ── Header bar ───────────────────────────────────────────────
        hdr_h = 44
        hdr   = pygame.Rect(pr.x, pr.y, pr.w, hdr_h)
        pygame.draw.rect(screen, (0, 40, 15), hdr)
        pygame.draw.line(screen, self.BORDER_COLOR,(pr.x, pr.y + hdr_h), (pr.x + pr.w, pr.y + hdr_h), 2)

        cursor_ch = "|" if self._blink else " "
        title_str = f"[ SYNTAX TERMINAL — {self.language.upper()} ]{cursor_ch}"
        title_surf = self._sysfont.render(title_str, True, self.TERM_COLOR)
        screen.blit(title_surf,(pr.x + pr.w // 2 - title_surf.get_width() // 2,pr.y + hdr_h // 2 - title_surf.get_height() // 2))

        # ── Prompt line ──────────────────────────────────────────────
        prompt = self._smfont.render(
            f"> SELECT THE CORRECT SYNTAX ANSWER:", True, (0, 180, 60))
        screen.blit(prompt, (pr.x + 20, pr.y + hdr_h + 10))

        # ── Question text (wrapped) ───────────────────────────────────
        q_lines = self._wrap_text(self._qtfont, self._current["q"], pr.w - 40)
        for li, line in enumerate(q_lines):
            surf = self._qtfont.render(line, True, (200, 255, 200))
            screen.blit(surf, (pr.x + 20, pr.y + hdr_h + 38 + li * 22))

        # ── Option buttons ───────────────────────────────────────────
        for i, opt_text in enumerate(self._current["options"]):
            rect     = self._option_rect(i)
            hovered  = rect.collidepoint(mouse_pos)
            flashing = (self._click_opt == i and
                        now - self._click_time < 120)
            is_answer = (i == self._current["answer"])

            # Background
            if self._feedback == "correct" and is_answer:
                bg = (0, 60, 20)
                bc = self.RIGHT_COLOR
            elif self._feedback == "wrong" and i == self._click_opt:
                bg = (60, 0, 0)
                bc = self.WRONG_COLOR
            elif flashing:
                bg = (0, 50, 20)
                bc = WHITE
            elif hovered and self._feedback is None:
                bg = (0, 40, 15)
                bc = self.TERM_COLOR
            else:
                bg = (10, 20, 10)
                bc = (0, 120, 40)

            pygame.draw.rect(screen, bg, rect)
            pygame.draw.rect(screen, bc, rect, 2)

            # Corner brackets
            blen = 7
            for sx, sy, dx, dy in [
                (-1,-1,1,0),(-1,-1,0,1),(1,-1,-1,0),(1,-1,0,1),
                (-1,1,1,0), (-1,1,0,-1),(1,1,-1,0), (1,1,0,-1),
            ]:
                ox = rect.centerx + sx*(rect.w//2)
                oy = rect.centery + sy*(rect.h//2)
                pygame.draw.line(screen, bc,(ox, oy), (ox+dx*blen, oy+dy*blen), 1)

            # Label + text
            label = self.OPTION_LABELS[i]
            lbl_s = self._sysfont.render(f"[{label}]", True, bc)
            screen.blit(lbl_s, (rect.x + 8, rect.centery - lbl_s.get_height()//2))

            # Wrap option text if needed
            opt_lines = self._wrap_text(
                self._smfont, opt_text, rect.w - lbl_s.get_width() - 24)
            for li2, ol in enumerate(opt_lines[:2]):
                os = self._smfont.render(ol, True, (180, 255, 180))
                screen.blit(os, (rect.x + lbl_s.get_width() + 16,rect.centery - (len(opt_lines[:2])*17)//2+ li2 * 17))

        # ── Feedback overlay ─────────────────────────────────────────
        if self._feedback is not None:
            fade = min(1.0, (now - self._feedback_time) / 200)
            if self._feedback == "correct":
                msg   = ">> CORRECT! SLIME ELIMINATED <<"
                color = self.RIGHT_COLOR
            else:
                msg   = ">> WRONG! -1 HP <<"
                color = self.WRONG_COLOR

            fb_surf = self._sysfont.render(msg, True, color)
            fx = pr.x + pr.w // 2 - fb_surf.get_width()  // 2
            fy = pr.y + pr.h - 38
            # Glow box
            glow = pygame.Surface((fb_surf.get_width()+24, fb_surf.get_height()+12),pygame.SRCALPHA)
            glow.fill((*color[:3], 40))
            screen.blit(glow, (fx - 12, fy - 6))
            screen.blit(fb_surf, (fx, fy))
            
            
def draw_hp_bar(screen: pygame.Surface, player, font: PixelFont):
    """Cyberpunk-style animated HP bar with hearts, glow, and danger flash."""
    now      = pygame.time.get_ticks()
    bar_x    = 16
    bar_y    = 16
    heart_sz = 22
    gap      = 8

    # ── Background panel ────────────────────────────────────────────
    panel_w = heart_sz * player.max_hp + gap * (player.max_hp - 1) + 90
    panel_h = 36
    panel   = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 140))
    pygame.draw.rect(panel, (0, 180, 60, 80), (0, 0, panel_w, panel_h), 1)
    screen.blit(panel, (bar_x - 6, bar_y - 4))

    # ── "HP" label ───────────────────────────────────────────────────
    font.render("HP", screen, bar_x, bar_y + 7, color=(0, 255, 100))
    lw   = font.text_width("HP")
    hx   = bar_x + lw + 12

    # ── Danger pulse (flashes red when hp == 1) ───────────────────────
    danger   = player.hp == 1
    pulse    = abs((now % 600) - 300) / 300   # 0→1→0 every 600ms
    low_glow = danger and pulse > 0.5

    for i in range(player.max_hp):
        cx = hx + heart_sz // 2 + i * (heart_sz + gap)
        cy = bar_y + heart_sz // 2 + 3
        alive = i < player.hp

        # ── Outer glow ring when alive ────────────────────────────────
        if alive:
            if danger:
                glow_col = (255, int(30 + pulse * 80), 30, int(40 + pulse * 60))
            else:
                glow_col = (0, 255, 100, 30)
            glow_s = pygame.Surface((heart_sz + 10, heart_sz + 10), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, glow_col,
                               ((heart_sz + 10) // 2, (heart_sz + 10) // 2),
                               heart_sz // 2 + 4)
            screen.blit(glow_s, (cx - (heart_sz + 10) // 2, cy - (heart_sz + 10) // 2))

        # ── Draw pixel heart ──────────────────────────────────────────
        # Pixel heart using a 7x6 grid scaled up
        pixel_map = [
            "0110110",
            "1111111",
            "1111111",
            "0111110",
            "0011100",
            "0001000",
        ]
        px_size = 3
        heart_surf = pygame.Surface((7 * px_size, 6 * px_size), pygame.SRCALPHA)

        if alive:
            if danger and low_glow:
                fill = (255, 60, 60)
                edge = (255, 150, 150)
            else:
                fill = (0, 220, 80)
                edge = (0, 255, 120)
        else:
            fill = (20, 40, 20)
            edge = (0, 60, 20)

        for row_i, row in enumerate(pixel_map):
            for col_i, px in enumerate(row):
                if px == "1":
                    # Inner fill
                    pygame.draw.rect(heart_surf, fill,
                                     (col_i * px_size + 1,
                                      row_i * px_size + 1,
                                      px_size - 1, px_size - 1))
                    # Edge highlight (top-left pixel of each block)
                    pygame.draw.rect(heart_surf, edge,
                                     (col_i * px_size,
                                      row_i * px_size, 1, 1))

        # Centre the heart at cx, cy
        hw = 7 * px_size
        hh = 6 * px_size
        screen.blit(heart_surf, (cx - hw // 2, cy - hh // 2))

        # ── Crack lines on empty hearts ───────────────────────────────
        if not alive:
            crack_col = (0, 80, 30)
            pygame.draw.line(screen, crack_col,
                             (cx - 3, cy - 4), (cx + 1, cy + 4), 1)
            pygame.draw.line(screen, crack_col,
                             (cx + 1, cy + 4), (cx + 4, cy), 1)

    # ── Low HP warning text ───────────────────────────────────────────
    if danger:
        warn_alpha = int(160 + pulse * 95)
        warn_surf  = pygame.Surface((100, 14), pygame.SRCALPHA)
        wfont = pygame.font.SysFont("courier", 11, bold=True)
        wtxt  = wfont.render("! LOW HP !", True, (255, int(40 + pulse*80), 40))
        wtxt.set_alpha(warn_alpha)
        wx = hx + player.max_hp * (heart_sz + gap) + 6
        screen.blit(wtxt, (wx + 25, bar_y + 9))       
# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    pygame.init()

    # --- Music ---
    def start_music():
        try:
            # Ensure mixer is initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 2048)

            music_dir = "GRAPHICS/Music/"
            # Get all files in the music directory
            music_files = [
                f for f in os.listdir(music_dir)
                if f.lower().endswith(('.mp3', '.wav', '.ogg'))
            ]

            if not music_files:
                print("[Music] No valid audio files found in GRAPHICS/Music/")
                return

            # Use the first found file
            music_path = os.path.join(music_dir, music_files[0])
            print(f"[Music] Loading: {music_path}")

            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)
            print("[Music] Playback started successfully.")

        except Exception as e:
            print(f"[Music] Error: {e}")

    # Start music immediately on launch
    start_music()


    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    bg_manager       = BackgroundManager()
    menu             = Menu()
    menu_bg = MenuBackground()
    player           = Player(-5, SCREEN_HEIGHT - 350)
    player.respawn_time = pygame.time.get_ticks()
    slime_group      = pygame.sprite.Group()
    world            = None
    game_over        = 0
    game_state       = MENU
    selected_language = None
    selected_level   = 1
    win_menu         = None
    pause_menu       = PauseMenu()
    world_map_screen = WorldMapScreen(total_levels=len(WORLD_DATA_LEVELS))
    paused           = False
    needs_reset      = False
    highest_unlocked = 1
    quiz_popup   : QuizPopup | None = None
    hud_font     = PixelFont(16)
    particles = ParticleManager(max_particles=300)

    game_over_screen = GameOverScreen()

    game_start_time : int | None = None
    deaths_count    : int        = 0
    hp_needs_reset = False   

    running = True
    while running:
        clock.tick(FPS)

        # -----------------------------------------------------------------
        # EVENT HANDLING
        # -----------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # --- MAIN MENU ---
            if game_state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
                chosen = menu.handle_click(pygame.mouse.get_pos())
                if chosen:
                    selected_language = chosen
                    slime_group.empty()
                    world      = World(WORLD_DATA_LEVELS[selected_level - 1], selected_level, slime_group)
                    game_state = PLAYING
                    pygame.mouse.set_visible(True)
                    if hp_needs_reset:
                        full_reset_game(player, slime_group, world, WORLD_DATA_LEVELS[selected_level - 1])
                        hp_needs_reset = False
                    else:
                        reset_game(player, slime_group, world, WORLD_DATA_LEVELS[selected_level - 1])
                    game_start_time = pygame.time.get_ticks()
                    deaths_count    = 0

            # --- WORLD MAP ---
            elif game_state == WORLD_MAP and event.type == pygame.MOUSEBUTTONDOWN:
                wm_choice = world_map_screen.handle_click(
                    pygame.mouse.get_pos(), highest_unlocked)
                if wm_choice == 0:           # Back → main menu
                    game_state = MENU
                    pygame.mouse.set_visible(False)
                elif wm_choice is not None:  # Level node clicked
                    selected_level = wm_choice
                    slime_group.empty()
                    world = World(WORLD_DATA_LEVELS[selected_level - 1],selected_level, slime_group)
                    if hp_needs_reset:
                        full_reset_game(player, slime_group, world, WORLD_DATA_LEVELS[selected_level - 1])
                        hp_needs_reset = False
                    else:
                        reset_game(player, slime_group, world, WORLD_DATA_LEVELS[selected_level - 1])
                    game_state      = PLAYING
                    game_over       = 0
                    game_start_time = pygame.time.get_ticks()
                    deaths_count    = 0
                    pygame.mouse.set_visible(True)
                    
            # --- QUIZ POPUP ---
            elif game_state == QUIZ and event.type == pygame.MOUSEBUTTONDOWN:
                if game_over == -1:
                    go_choice = game_over_screen.handle_click(pygame.mouse.get_pos())
                    if go_choice == 0:       # RETRY — full reset including HP
                        game_over       = 0
                        deaths_count   += 1
                        game_start_time = pygame.time.get_ticks()
                        quiz_popup      = None
                        game_state      = PLAYING
                        full_reset_game(player, slime_group, world,WORLD_DATA_LEVELS[selected_level - 1])
                        hp_needs_reset = False
                    elif go_choice == 1:     # WORLD MAP — position only, keep HP
                        game_state = WORLD_MAP
                        game_over  = 0
                        quiz_popup = None
                        pygame.mouse.set_visible(True)
                    elif go_choice == 2:     # MAIN MENU — position only, keep HP
                        game_state = MENU
                        game_over  = 0
                        quiz_popup = None
                        pygame.mouse.set_visible(False)
                elif quiz_popup:
                    quiz_popup.handle_click(pygame.mouse.get_pos())
                    
                    
                    
                    

            # --- PLAYING / WIN / PAUSED ---
            elif game_state in (PLAYING, WIN) or paused:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and game_state == PLAYING:
                        paused = not paused
                    elif event.key == pygame.K_r and game_over == -1:
                        game_over       = 0
                        deaths_count   += 1
                        game_start_time = pygame.time.get_ticks()
                        reset_game(player, slime_group, world,WORLD_DATA_LEVELS[selected_level - 1])

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()

                    # Game Over screen clicks
                    if game_state == PLAYING and game_over == -1 and not paused:
                        go_choice = game_over_screen.handle_click(mouse)
                        if go_choice == 0:   # RETRY
                            game_over       = 0
                            deaths_count   += 1
                            game_start_time = pygame.time.get_ticks()
                            full_reset_game(player, slime_group, world, WORLD_DATA_LEVELS[selected_level-1])  
                            hp_needs_reset = False# ← full
                        elif go_choice == 1:  # WORLD MAP  ← ADD THIS
                            game_state = WORLD_MAP
                            game_over  = 0
                            paused     = False
                            pygame.mouse.set_visible(True)
                        elif go_choice == 2:  # MAIN MENU
                            game_state = MENU
                            game_over  = 0
                            paused     = False
                            pygame.mouse.set_visible(False)

                    # Win menu clicks
                    elif game_state == WIN and win_menu and not paused:
                        choice = win_menu.handle_click(mouse)
                        if choice == 0:    # NEXT LEVEL
                            next_lvl = selected_level + 1
                            if next_lvl <= len(WORLD_DATA_LEVELS):
                                selected_level   = next_lvl
                                highest_unlocked = max(highest_unlocked, selected_level)
                                slime_group.empty()
                                world = World(WORLD_DATA_LEVELS[selected_level - 1],selected_level, slime_group)
                                reset_game(player, slime_group, world,WORLD_DATA_LEVELS[selected_level - 1])
                                game_state      = PLAYING
                                game_over       = 0
                                win_menu        = None
                                game_start_time = pygame.time.get_ticks()
                                deaths_count    = 0
                        elif choice == 1:  # WORLD MAP
                            game_state = WORLD_MAP
                            win_menu   = None
                            game_over  = 0
                            paused     = False
                            pygame.mouse.set_visible(True)
                        elif choice == 2:  # MAIN MENU
                            game_state  = MENU
                            win_menu    = None
                            game_over   = 0
                            paused      = False
                            needs_reset = True
                            pygame.mouse.set_visible(False)

                    # Pause menu clicks
                    elif paused:
                        choice = pause_menu.handle_click(mouse)
                        if choice == 0:        # CONTINUE
                            paused = False
                        elif choice == 1:      # MAIN MENU
                            game_state = MENU
                            paused     = False
                            win_menu   = None
                            pygame.mouse.set_visible(False)
                        elif choice == 2:    # RESET
                            game_over  = 0
                            paused     = False
                            game_state = PLAYING
                            full_reset_game(player, slime_group, world, WORLD_DATA_LEVELS[selected_level-1])
                            hp_needs_reset = False# ← full
                        elif choice == 4:      # WORLD MAP  ← ADD THIS
                            game_state = WORLD_MAP
                            paused     = False
                            win_menu   = None
                            pygame.mouse.set_visible(True)

        # -----------------------------------------------------------------
        # UPDATE
        # -----------------------------------------------------------------
        if game_state == WORLD_MAP:
            world_map_screen.update()
            
        if game_state == MENU:
            menu_bg.update()
            
                # Check if player touched a slime → open quiz
        if (game_state == PLAYING and game_over == 0 and not paused and player.quiz_trigger_slime is not None):
            game_state = QUIZ
            quiz_popup = QuizPopup(selected_language or "Python")
            pygame.mouse.set_visible(True)

        # Quiz update
        if game_state == QUIZ and quiz_popup:
            quiz_popup.update()
            if quiz_popup.done:
                if quiz_popup.result == "correct":
                    if player.quiz_trigger_slime is not None:
                        if player.quiz_trigger_slime in slime_group:
                            # ← emit slime death effect at the slime's position
                            particles.emit_slime(player.quiz_trigger_slime.rect.centerx,
                                                player.quiz_trigger_slime.rect.centery)
                            player.quiz_trigger_slime.kill()
                    player.quiz_trigger_slime = None
                    player.respawn_time       = pygame.time.get_ticks()
                    quiz_popup                = None
                    game_state                = PLAYING
                    pygame.mouse.set_visible(True)
                else:
                    # Wrong — lose HP then immediately show a new question
                    player.hp -= 1
                    particles.emit_death(player.rect.centerx, player.rect.centery)
                    if player.hp <= 0:
                        # No HP left — close terminal and trigger game over
                        player.quiz_trigger_slime = None
                        quiz_popup                = None
                        game_state                = PLAYING
                        game_over                 = -1
                        hp_needs_reset            = True
                        pygame.mouse.set_visible(True)
                    else:
                        # Still alive — spawn a fresh terminal immediately
                        quiz_popup = QuizPopup(selected_language or "Python")

        if game_state == PLAYING and game_over == 0 and not paused:
            result = player.update(world, game_over, slime_group)
            if result == -1 and game_over != -1:
                hp_needs_reset = True   # ← add
            game_over = result

            if not player.is_dying:
                slime_group.update(world)

            world.gate_group.update()
            for gate in world.gate_group:
                if player.hitbox.colliderect(gate.hitbox):
                    gate.trigger()
                if gate.is_open:
                    particles.emit_gate(gate.rect.x, gate.rect.y)
                    next_lvl = selected_level + 1
                    if next_lvl <= len(WORLD_DATA_LEVELS):
                        # More levels remain — show win screen
                        highest_unlocked = max(highest_unlocked, next_lvl)
                        game_state = WIN
                        win_menu   = None   # fresh instance each time
                    else:
                        # All levels done — show win screen for final level
                        highest_unlocked = max(highest_unlocked, selected_level)
                        game_state = WIN
                        win_menu   = None
                    break  # stop checking gates once one is open

        # -----------------------------------------------------------------
        # DRAW
        # -----------------------------------------------------------------
        screen.fill(BLACK)

        if game_state == MENU:
            menu.draw(screen, pygame.mouse.get_pos(), menu_bg)
            
        

        elif game_state == WORLD_MAP:
            world_map_screen.draw(screen, pygame.mouse.get_pos(), highest_unlocked)
            pygame.mouse.set_visible(True)

        elif game_state == PLAYING:
            bg_manager.draw(screen)
            world.draw(screen)
            for enemy in slime_group:
                enemy.draw(screen)
            player.draw(screen)
            draw_hp_bar(screen, player, hud_font)
            
            if game_over == -1:
                if game_start_time is not None:
                    game_over_screen.elapsed_secs = (
                        pygame.time.get_ticks() - game_start_time) // 1000
                game_over_screen.deaths = deaths_count
                game_over_screen.draw(screen, pygame.mouse.get_pos())
                
            if paused:
                pause_menu.draw(screen, pygame.mouse.get_pos())
                pygame.mouse.set_visible(True)
                    
        elif game_state == QUIZ:
            bg_manager.draw(screen)
            world.draw(screen)
            for enemy in slime_group:
                enemy.draw(screen)
            player.draw(screen)
            draw_hp_bar(screen, player, hud_font)
            if quiz_popup:
                quiz_popup.draw(screen, pygame.mouse.get_pos())
            pygame.mouse.set_visible(True)

            if game_over == -1:
                if game_start_time is not None:
                    game_over_screen.elapsed_secs = (pygame.time.get_ticks() - game_start_time) // 1000
                game_over_screen.deaths = deaths_count
                game_over_screen.draw(screen, pygame.mouse.get_pos())

            if paused:
                pause_menu.draw(screen, pygame.mouse.get_pos())
                pygame.mouse.set_visible(True)

        elif game_state == WIN:
            bg_manager.draw(screen)
            world.draw(screen)
            for enemy in slime_group:
                enemy.draw(screen)
            player.draw(screen)
            particles.draw(screen)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            if win_menu is None:
                win_menu = WinMenu()

            if not paused:
                win_menu.draw(screen, pygame.mouse.get_pos())
            else:
                pause_menu.draw(screen, pygame.mouse.get_pos())

            pygame.mouse.set_visible(True)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()