import streamlit as st
import streamlit.components.v1 as components

from streamlit_drawable_canvas import st_canvas
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io

import json

import gspread
from google.oauth2.service_account import Credentials

import os
import datetime

import math
import re

def render_gcf_factorization(item):
    st.write(item["text"])

    gcf_key = f"{item['id']}_gcf"

    def first_two_factors(n):
        factors = []
        for i in range(1, n + 1):
            if n % i == 0:
                factors.append(i)
            if len(factors) == 2:
                break
        return factors

    factors_n1 = first_two_factors(item["num1"])
    factors_n2 = first_two_factors(item["num2"])
    
    st.text_input(f"Factors of {item['num1']} (comma separated):", key=f"{item['id']}_factors_n1", placeholder=f"e.g., {', '.join(map(str, factors_n1))}...")
    st.text_input(f"Factors of {item['num2']} (comma separated):", key=f"{item['id']}_factors_n2", placeholder=f"e.g., {', '.join(map(str, factors_n2))}...")

    st.text_input("GCF:", placeholder="Enter a whole number (e.g., 2)", key=gcf_key)

def render_gcf_subtraction(item):
    st.write(item["text"])

    steps_key = f"{item['id']}_steps"
    input_key = f"{item['id']}_input"
    error_key = f"{item['id']}_error"
    gcf_key = f"{item['id']}_gcf"

    bigger = max(item["num1"], item["num2"])
    smaller = min(item["num1"], item["num2"])

    # Init session state
    if steps_key not in st.session_state:
        st.session_state[steps_key] = []

    if error_key not in st.session_state:
        st.session_state[error_key] = ""

    def add_step():
        raw = st.session_state[input_key].strip()
        try:
            num, den = map(int, raw.split("-"))
            st.session_state[steps_key].append(f"{num} - {den} = {num - den}")
            st.session_state[input_key] = ""
            st.session_state[error_key] = ""
        except:
            st.session_state[error_key] = f"❌ Invalid format. Use e.g., {bigger}-{smaller}"

    def remove_step():
        if st.session_state[steps_key]:
            st.session_state[steps_key].pop()

    # Show current steps
    for step in st.session_state[steps_key]:
        st.text(step)

    st.text_input(f"Type a subtraction step (e.g., {bigger}-{smaller})", key=input_key)
    if st.session_state[error_key]:
        st.warning(st.session_state[error_key])

    cols = st.columns([1.5, 6])
    with cols[0]:
        st.button("Add subtraction step", on_click=add_step, key=f"{item['id']}_add_btn")
    with cols[1]:
        st.button("Remove last step", on_click=remove_step, key=f"{item['id']}_remove_btn")

    st.text_input("GCF:", placeholder="Enter a whole number (e.g., 2)", key=gcf_key)

def render_gcf_division(item):
    st.write(item["text"])

    steps_key = f"{item['id']}_steps"
    input_key = f"{item['id']}_input"
    error_key = f"{item['id']}_error"
    gcf_key = f"{item['id']}_gcf"

    bigger = max(item["num1"], item["num2"])
    smaller = min(item["num1"], item["num2"])

    if steps_key not in st.session_state:
        st.session_state[steps_key] = []
    if error_key not in st.session_state:
        st.session_state[error_key] = ""

    def add_step():
        raw = st.session_state[input_key].strip()
        try:
            num, den = map(int, raw.split("/"))
            if den == 0:
                st.session_state[error_key] = "❌ Division by zero is not allowed."
                return
            quotient = num // den
            remainder = num % den
            st.session_state[steps_key].append(f"{num} ÷ {den} = {quotient} R {remainder}")
            st.session_state[input_key] = ""
            st.session_state[error_key] = ""
        except:
            st.session_state[error_key] = f"❌ Invalid format. Use e.g., {bigger}/{smaller}"

    def remove_step():
        if st.session_state[steps_key]:
            st.session_state[steps_key].pop()

    # Show steps
    for step in st.session_state[steps_key]:
        st.text(step)

    st.text_input(f"Type a division step (e.g., {bigger}/{smaller})", key=input_key)
    if st.session_state[error_key]:
        st.warning(st.session_state[error_key])

    cols = st.columns([1.5, 6])
    with cols[0]:
        st.button("Add division step", on_click=add_step, key=f"{item['id']}_add_btn")
    with cols[1]:
        st.button("Remove last step", on_click=remove_step, key=f"{item['id']}_remove_btn")

    st.text_input("GCF:", placeholder="Enter a whole number (e.g., 2)", key=gcf_key)

def render_instruction(item):
    st.write(f"**Instruction**: {item['text']}")
    if "image" in item:
        st.image(item["image"])

def render_mcq(item):
    question_text = item["text"]
    options = [f"{chr(97 + i)}. {opt}" for i, opt in enumerate(item["options"])]
    
    st.write(question_text)
    if "image" in item:
        st.image(item["image"])

    st.radio(
        f"**{question_text}**",
        options=options,
        key=item["id"],
        label_visibility="collapsed"
    )

# def render_short_answer(item):
#     st.write(item["text"])
#     st.text_input(label=item["text"], key=item["id"], label_visibility="collapsed")
#     st.write("")

def render_custom_component(item, components):
    st.write(item["text"])
    component_name = item["component"]
    
    if component_name in components:
        component = components[component_name]
        global user_board
        user_board = component(key=item["id"])
    else:
        st.warning(f"Unknown component: {component_name}")

def render_drawing(item):
    st.write(f"**Instruction**: {item['text']}")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 1)",  # White background
        stroke_width=3,
        stroke_color="black",
        background_color="white",
        height=600,
        width=700,
        drawing_mode="freedraw",  # or "line", "rect", "circle", "transform"
        key="canvas",
    )

def render_short_answer(item):
    st.write(item["text"])
    st.text_input("Nodes (separated by commas):", key = item["id"])

def render_graph_visualization(item):
    st.write(item["text"])
    
    col1, col2 = st.columns([2, 5])
    with col1:
        edge_0 = st.text_input(f"Edge 1", key=f"edge_0", label_visibility="collapsed")
        edge_inputs = [edge_0] + [st.text_input(f"Edge {i+1}", key=f"edge_{i}", label_visibility="collapsed")
                for i in range(1, 7)]

    edges = [e.strip() for e in edge_inputs if e and "-" in e]

    # Build undirected graph
    G = nx.Graph()
    for e in edges:
        n1, n2 = [s.strip().capitalize() for s in e.split("-", 1)]
        G.add_edge(n1, n2)

    with col2:
        # st.subheader("Friendship Network Visualization")

        if G.number_of_edges() > 0:
            # Draw undirected graph with matplotlib
            plt.figure(figsize=(8, 6))
            pos = nx.spring_layout(G)  # Force-directed layout for nice visualization
            nx.draw(G, pos, with_labels=True, node_color="skyblue", edge_color="gray", node_size=2000, font_size=12)
            st.pyplot(plt)
        else:
            st.info("Enter valid edges to visualize the friendship network.")

def render_item(item, components=None):
    match item["type"]:
        case "mcq":
            render_mcq(item)
        case "short_answer":
            render_short_answer(item)
        case "instruction":
            render_instruction(item)
        case "sudoku":
            render_custom_component(item, components)
        case "gcf_factorization":
            render_gcf_factorization(item)
        case "gcf_subtraction":
            render_gcf_subtraction(item)
        case "gcf_division":
            render_gcf_division(item)
        case "drawing":
            render_drawing(item)
        case "graph_visualization":
            render_graph_visualization(item)
        case _:
            st.warning(f"Unknown item type: {item['type']}")

    st.write("")  # Spacer
    st.write("")  # One more

def render_section(section, components=None):
    st.subheader(section["title"])
    
    if "instruction" in section:
        st.write(f"**Instruction**: {section['instruction']}")
    if "image" in section:
        st.image(section["image"])
    
    for item in section.get("items", []):
        render_item(item, components)

def render_exam(exam_data, components=None):
    st.title(exam_data.get("title", "Exam"))

    for section in exam_data.get("sections", []):
        render_section(section, components)



st.set_page_config(page_title="Final Exam", layout="centered")
st.title("Final Exam")
st.header("Student Information")

# Student Info
class_options = ["3/11", "3/12"]
selected_class = st.selectbox("Select your class:", class_options)
nickname = st.text_input("Nickname")
roll_number = st.text_input("Roll Number")

# Load your JSON
with open("exam.json") as f:
    exam_data = json.load(f)

# Declare components
# sudoku = components.declare_component("sudoku", path="components/sudoku")
# custom_components = {
#     "sudoku": sudoku
# }

sudoku_a = components.declare_component(
    "sudoku_a",
    path="components/sudoku/set_a"
)

sudoku_b = components.declare_component(
    "sudoku_b",
    path="components/sudoku/set_b"
)

custom_components = {
    "sudoku_a": sudoku_a,
    "sudoku_b": sudoku_b
}

user_board = []

# Render everything
render_exam(exam_data, components=custom_components)


def grade_sudoku(user_board, puzzle, solution, board_size, max_points):
    total = correct = 0
    if not user_board:
        return 0
    for i in range(board_size):
        for j in range(board_size):
            if puzzle[i][j] == 0:
                total += 1
                if user_board[i][j] == solution[i][j]:
                    correct += 1
    return round(correct / total * max_points, 2) if total else 0

def grade_factorization(raw_gcf, user_raw_n1, user_raw_n2, num1, num2, max_points):
    # Helper: extract factors as a set of ints
    def extract_factors(raw_input):
        import re
        matches = re.findall(r'\d+(?:\.0+)?', raw_input)
        factors = set()
        for m in matches:
            num = float(m)
            if num.is_integer():
                factors.add(int(num))
        return factors

    user_factors_n1 = extract_factors(user_raw_n1)
    user_factors_n2 = extract_factors(user_raw_n2)

    # Correct factors sets
    def all_factors(n):
        return set(i for i in range(1, n + 1) if n % i == 0)
    
    correct_n1 = all_factors(num1)
    correct_n2 = all_factors(num2)

    # Score per number (half points each)
    def score_for_side(user_factors, correct_factors):
        if not user_factors:
            return 0
        correct = len(user_factors & correct_factors)
        wrong = len(user_factors - correct_factors)
        total = len(correct_factors)
        # Partial credit formula: correct minus penalty for wrong, minimum 0
        raw_score = (correct - wrong) / total
        return max(0, raw_score)

    score_n1 = score_for_side(user_factors_n1, correct_n1)
    score_n2 = score_for_side(user_factors_n2, correct_n2)

    # GCF grading
    correct_gcf = math.gcd(num1, num2)
    gcf_score = 0
    try:
        gcf_value = list(extract_factors(raw_gcf))
        if gcf_value and gcf_value[0] == correct_gcf:
            gcf_score += max_points / 2
    except:
        pass

    # total_score = 0.5 * (score_n1 + score_n2) + gcf_score
    factor_score = ((score_n1 + score_n2) / 2) * (max_points / 2)

    total_score = factor_score + gcf_score
    return round(total_score, 2)

def compute_euclidean_subtraction_steps(a, b):
    steps = []
    while a != b:
        bigger = max(a, b)
        smaller = min(a, b)
        diff = bigger - smaller
        steps.append(f"{bigger} - {smaller} = {diff}")
        a, b = smaller, diff
    return steps  # Final step excluded intentionally

def compute_euclidean_division_steps(num1, num2):
    """Generate expected division steps using Euclidean algorithm with division."""
    bigger, smaller = max(num1, num2), min(num1, num2)
    steps = []
    while smaller != 0:
        quotient = bigger // smaller
        remainder = bigger % smaller
        steps.append(f"{bigger} ÷ {smaller} = {quotient} R {remainder}")
        bigger, smaller = smaller, remainder
    return steps

def grade_gcf(item, session_state, max_points, compute_steps_fn):
    item_id = item["id"]
    num1, num2 = item["num1"], item["num2"]
    correct_gcf = math.gcd(num1, num2)

    user_gcf_raw = session_state.get(f"{item_id}_gcf", "").strip()
    user_steps = session_state.get(f"{item_id}_steps", [])
    user_input_raw = session_state.get(f"{item_id}_input", "").strip()

    correct_steps = compute_steps_fn(num1, num2)
    total_correct = len(correct_steps)

    if total_correct == 0 or num1 == num2 or num1 == 0 or num2 == 0:
        # No steps, all points to GCF
        gcf_points = max_points
        step_points = 0
        unit_score = 0
    else:
        gcf_points = step_points = max_points / 2
        unit_score = step_points / total_correct

    gcf_score = 0
    try:
        if int(float(user_gcf_raw)) == correct_gcf or int(float(user_input_raw)) == correct_gcf:
            gcf_score = gcf_points
    except:
        pass

    step_score = 0
    for i in range(min(len(user_steps), total_correct)):
        if user_steps[i] == correct_steps[i]:
            step_score += unit_score
        else:
            break  # stop at first wrong step

    total_score = round(gcf_score + step_score, 2)
    return total_score

def grade_node_list(user_input, expected_nodes, max_points):
    if not user_input:
        return 0

    user_nodes = {n.strip().capitalize() for n in user_input.split(",")}
    correct = len(user_nodes & set(expected_nodes))
    wrong = len(user_nodes - set(expected_nodes))
    total = len(expected_nodes)

    score = max((correct - wrong) / total, 0)
    return round(score * max_points, 2)

def grade_edge_list(edge_inputs, expected_edges, max_points):
    parsed_edges = set()

    for e in edge_inputs:
        if "-" in e:
            n1, n2 = [s.strip().capitalize() for s in e.split("-", 1)]
            parsed_edges.add(tuple(sorted((n1, n2))))

    expected_set = {tuple(sorted(e)) for e in expected_edges}

    correct = len(parsed_edges & expected_set)
    wrong = len(parsed_edges - expected_set)
    total = len(expected_set)

    score = max((correct - wrong) / total, 0)
    return round(score * max_points, 2)


def grade_exam():
    total_score = 0
    section_counter = 1

    submission = {
        "roll_number": roll_number,
        "nickname": nickname,
        "class": selected_class,
        "timestamp": timestamp,
        "answers": {},
        "scores": {},
    }
    for section in exam_data.get("sections", []):
        section_name = f"part{section_counter}"
        section_score = 0
        
        submission["answers"][section_name] = {}

        for item in section.get("items", []):
            item_id = item.get("id")
            if not item_id:
                continue

            item_type = item["type"]
            max_points = item.get("max_points", 0)

            # Auto-grading logic
            if item_type == "mcq":
                
                # max_points = item.get("max_points", 0)

                student_answer = st.session_state.get(item_id, "")

                correct = st.secrets["answers"][item_id]
                if student_answer.startswith(correct):  # e.g., "b. 4"
                    section_score += max_points
            
                # Store student answer
                submission["answers"][section_name][item_id] = {
                    "answer": student_answer,
                    "type": item_type
                }

            elif item_type == "sudoku":
                puzzle = st.secrets["sudoku"]["puzzle"]
                solution = st.secrets["sudoku"]["solution"]
                
                board_size = len(puzzle)

                # max_points = item.get("max_points", 0)
                score = grade_sudoku(user_board, puzzle, solution, board_size, max_points)
                section_score += score

                submission["answers"][section_name][item_id] = {
                    "answer": user_board,
                    "type": "sudoku",
                    "score": score
                }

            elif item_type == "gcf_factorization":
                

                num1, num2 = item["num1"], item["num2"]

                # Inputs
                raw_factors1 = st.session_state.get(f"{item_id}_factors_n1", "")
                raw_factors2 = st.session_state.get(f"{item_id}_factors_n2", "")
                raw_gcf = st.session_state.get(f"{item_id}_gcf", "")

                # score = grade_gcf_factorization(item, st.session_state, max_points)
                score = grade_factorization(raw_gcf, raw_factors1, raw_factors2, num1, num2, max_points)
                
                submission["answers"][section_name][item_id] = {
                    "factors_n1": st.session_state.get(f"{item_id}_factors_n1", ""),
                    "factors_n2": st.session_state.get(f"{item_id}_factors_n2", ""),
                    "gcf": st.session_state.get(f"{item_id}_gcf", ""),
                    "type": item_type,
                    "score": score
                }

                section_score += score

            elif item_type == "gcf_subtraction":
                
                score = grade_gcf(item, st.session_state, max_points, compute_euclidean_subtraction_steps)

                submission["answers"][section_name][item_id] = {
                    "gcf": st.session_state.get(f"{item_id}_gcf", ""),
                    "input": st.session_state.get(f"{item_id}_input", ""),
                    "steps": st.session_state.get(f"{item_id}_steps", []),
                    "type": item_type,
                    "score": score
                }

                section_score += score

            elif item_type == "gcf_division":
                
                score = grade_gcf(item, st.session_state, max_points, compute_euclidean_division_steps)

                submission["answers"][section_name][item_id] = {
                    "gcf": st.session_state.get(f"{item_id}_gcf", ""),
                    "input": st.session_state.get(f"{item_id}_input", ""),
                    "steps": st.session_state.get(f"{item_id}_steps", []),
                    "type": item_type,
                    "score": score
                }

                section_score += score

            elif item_type == "short_answer" and item_id == "q19":
                user_nodes = st.session_state.get(item_id, "")
                expected_nodes = st.secrets["answers"][item_id]
                score = grade_node_list(user_nodes, expected_nodes, max_points)

                submission["answers"][section_name][item_id] = {
                    "answer": user_nodes,
                    "score": score,
                    "type": item_type
                }
                section_score += score

            elif item_type == "graph_visualization" and item_id == "q20":
                edges = [st.session_state.get(f"edge_{i}", "") for i in range(7)]
                expected_edges = [
                    ["Fah", "Beam"],
                    ["Fah", "New"],
                    ["Fah", "Win"],
                    ["Beam", "Tae"],
                    ["New", "Win"],
                    ["New", "Tae"],
                    ["Win", "Tae"]
                ]
                score = grade_edge_list(edges, expected_edges, max_points)

                submission["answers"][section_name][item_id] = {
                    "edges": edges,
                    "score": score,
                    "type": item_type
                }
                section_score += score



        
        submission["scores"][section_name] = section_score
        total_score += section_score
        section_counter += 1

    submission["scores"]["total"] = total_score
    return submission










if st.button("Submit Test"):
    if not nickname or not roll_number:
        st.error("Please fill in your nickname and roll number.")
    else:
        
        

        # Set up creds and open your sheet
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # Load credentials from Streamlit secrets
        service_account_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        
        client = gspread.authorize(creds)
        
        
        # Timestamp for filenames and sheets
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # st.write("Session Debug", st.session_state)
        
        submission = grade_exam()

        json_path = f'{selected_class.replace("/", "-")}_{nickname}_{roll_number}_{filename_ts}.json'
        with open(json_path, "w") as f:
            json.dump(submission, f, indent=2)
            
        

        try:
            sheet = client.open("Midterm").worksheet(selected_class)
        except gspread.WorksheetNotFound:
            st.error(f"Worksheet '{selected_class}' not found. Please check your Google Sheet.")

        row = [
            submission["roll_number"],
            submission["nickname"],
            submission["scores"]["part1"],
            submission["scores"]["part2"],
            submission["scores"]["part3"],
            submission["scores"]["total"],
            timestamp
        ]

        sheet.append_row(row)
        st.success(f"Submission received! ✅ Total Score: {round(submission['scores']['total'])}/20")
        
        with open(json_path, "rb") as f:
            st.download_button(
            "Download answers",
                data=f,
                file_name=os.path.basename(json_path),
                mime="application/json"
            )

