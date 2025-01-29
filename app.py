import streamlit as st
import time
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances
import google.generativeai as genai
import random
import os
import ast


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model_bio = genai.GenerativeModel('gemini-1.5-flash')


# Example dataset
example_data = pd.read_csv('Dataset/synthetic_user_data.csv')
# Convert the column of strings to actual lists
example_data['EMBEDDING'] = example_data['EMBEDDING'].apply(ast.literal_eval)

# Optional: Convert lists to numpy arrays for efficient computation
example_data['EMBEDDING'] = example_data['EMBEDDING'].apply(np.array)


def generate_embedding(bio):
    # Dummy embedding: convert bio to vector of word counts
    print(bio)
    EMBEDDING = genai.embed_content(model="models/text-embedding-004",
                                    content=bio)
    return np.array(EMBEDDING['embedding'])

# def generate_content(prompt: str) -> str:
#     """
#     Placeholder function for an LLM-based content generator.
#     Replace with a real API call to OpenAI or another LLM.
#     """
#     time.sleep(1)  # simulate LLM latency
#     return f"[Mediator LLM Intro Based on Prompt: {prompt}]"

def find_nearest_neighbors(user_bio, dataset, n_neighbors=6):
    # Generate embedding for the user's bio
    EMBEDDING = genai.embed_content(model="models/text-embedding-004",
                            content=user_bio)
    user_embedding = np.array(EMBEDDING['embedding'])

    # Generate embeddings for the dataset
    dataset_embeddings = np.vstack(dataset['EMBEDDING'].values)


    # Compute distances (cosine distances)
    distances = euclidean_distances([user_embedding], dataset_embeddings).flatten()
    
    # Find the indices of the nearest neighbors
    nearest_indices = distances.argsort()[:n_neighbors]

    return dataset.iloc[nearest_indices], user_embedding


###################################
# 2) STREAMLIT MULTI-PAGE LOGIC   #
###################################

# We'll store stateful info in st.session_state
if 'page' not in st.session_state:
    st.session_state['page'] = "Sign-Up Page"
if 'processing_done' not in st.session_state:
    st.session_state['processing_done'] = False
if 'support_group' not in st.session_state:
    st.session_state['support_group'] = None
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'introduction' not in st.session_state:
    st.session_state['introduction'] = None
if 'user_bio' not in st.session_state:
    st.session_state['user_bio'] = ""
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'ellie_already_suggested_topic' not in st.session_state:
    st.session_state['ellie_already_suggested_topic'] = False


def navigate(page_name: str):
    st.session_state['page'] = page_name
    st.rerun()

###############################
# 3) PAGE: SIGN-UP FORMS      #
###############################
def sign_up_page():
    st.title("Sign-Up to SafeCircle to Find Your Support Network")

    name = st.text_input("Name")
    age = st.number_input("Age", min_value=18, max_value=100, step=1)
    gender = st.selectbox("Gender", ["--Please Select--", "Male", "Female", "Non-binary", "Prefer not to say"])
    bio = st.text_area("Write a brief bio about yourself. We will use this to find you the best matches.")

    if st.button("Submit"):
        if len(bio.strip()) == 0:
            st.warning("Please fill out the bio field.")
        else:
            st.session_state['user_name'] = name
            st.session_state['user_bio'] = bio
            st.session_state['processing_done'] = False
            navigate("Loading Page")

########################################
# 4) PAGE: LOADING (p5.js ANIMATION)   #
########################################
def loading_page():
    st.title("Finding Your Support Group...")
    st.write("We are processing your information to find the best match.")

    # p5.js network/ball-and-stick animation
    animation_html = """
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js"></script>
    </head>
    <body>
        <script>
            let points = [];
            let edges = [];
            let settled = false;
            let maxAge = 100;  // Maximum age for unstable edges

            function setup() {
                createCanvas(600, 400);

                // Initialize random points
                for (let i = 0; i < 70; i++) {
                    points.push({
                        x: random(width),
                        y: random(height),
                        vx: random(-1.0, 1.0),
                        vy: random(-1.0, 1.0)
                    });
                }
                
                // Initialize edges with random ages
                for (let i = 0; i < 100; i++) {
                    edges.push({
                        start: int(random(points.length)),
                        end: int(random(points.length)),
                        age: random(maxAge),
                        stable: random(1) < 0.2
                    });
                }
            }

            function draw() {
                background(30);
                strokeWeight(2);

                // Draw edges
                for (let edge of edges) {
                    let p1 = points[edge.start];
                    let p2 = points[edge.end];
                    // stable edges = green, unstable edges = grey
                    if (edge.age > 0 || edge.stable) {
                        stroke(edge.stable ? color(0, 255, 0, 150) : color(200, 150));
                        line(p1.x, p1.y, p2.x, p2.y);
                        edge.age--;
                    }
                }

                // Remove old edges and add new ones randomly
                edges = edges.filter(e => e.age > 0 || e.stable);
                if (frameCount % 15 === 0 && !settled) {
                    edges.push({
                        start: int(random(points.length)),
                        end: int(random(points.length)),
                        age: random(maxAge),
                        stable: random(1) < 0.2
                    });
                }

                // Draw points
                noStroke();
                fill(255, 100, 100);
                for (let p of points) {
                    ellipse(p.x, p.y, 8, 8);
                    if (!settled) {
                        p.x += p.vx;
                        p.y += p.vy;
                        // slow down
                        p.vx *= 0.99;
                        p.vy *= 0.99;

                        // bounce if hitting edges
                        if (p.x < 0 || p.x > width) p.vx *= -1;
                        if (p.y < 0 || p.y > height) p.vy *= -1;
                    }
                }

                // after 300 frames, "settle"
                if (!settled && frameCount > 300) {
                    settled = true;
                    for (let p of points) {
                        p.vx = 0;
                        p.vy = 0;
                    }
                }
            }
        </script>
    </body>
    </html>
    """

    st.components.v1.html(animation_html, height=400)

    # Simulate “async” embedding + neighbor search
    if not st.session_state['processing_done']:
        # We'll break it into small steps so that the UI can update
        with st.spinner("Analysing your bio and finding support group..."):
            time.sleep(2)  # short delay
            neighbors, user_embedding = find_nearest_neighbors(
                st.session_state['user_bio'], example_data, n_neighbors=6
            )
            st.session_state['support_group'] = neighbors
            # Generate an intro from mediator LLM
            combined_bios = "\n".join(neighbors['BIO'].astype(str))
            introduction_prompt = f"""
            Your name is Ellie and you are mediating a mental health support group.
            Write a brief summary introductory message to bring the group together 
            using the following self-written bios:
            {combined_bios}. Do not write out the actual bios themselves. You
            are just a friendly and personable member of the group going to guide them.
            """
            introduction = model_bio.generate_content(introduction_prompt)
            st.session_state['introduction'] = introduction.text
            st.session_state['processing_done'] = True
        
        # Once done, go to next page
        navigate("Welcome Screen")

##############################################
# 5) PAGE: WELCOME SCREEN (Fade-In Message)  #
##############################################
def welcome_page():
    st.title("Welcome!")
    fade_in_html = """
    <html>
    <head>
        <style>
            body {
                background-color: #1e1e1e;
                color: white;
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 150px;
            }
            .fade-in {
                opacity: 0;
                animation: fadeIn 3s forwards;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        </style>
    </head>
    <body>
        <h1 class="fade-in">We've found you a group.<br>Welcome to SafeCircle.</h1>
    </body>
    </html>
    """
    st.components.v1.html(fade_in_html, height=400)
    
    # Wait 3 seconds, then go to group board
    time.sleep(5)
    navigate("Group Messaging Board")

def group_messaging_board():
    st.title("Group Messaging Board")
    st.subheader("Your Group Members:")
    if st.session_state['support_group'] is not None:
        for user in st.session_state['support_group']['USERNAME']:
            st.write(f"- {user}")

    st.divider()

    # ============ CREATE "BUBBLE" STYLING FUNCTION ===========
    def render_message_bubble(username, text):
        """
        Renders a single message bubble with different colors
        depending on the 'username'.
        - "Ellie": purple background
        - current user: green background
        - others: blue background
        """
        if username.lower() == "ellie":
            bg_color = "#9b59b6"  # purple
            text_color = "white"
        elif username == st.session_state['user_name']:
            bg_color = "#2ecc71"  # green
            text_color = "white"
        else:
            bg_color = "#3498db"  # blue
            text_color = "white"
        
        # Inline HTML for bubble
        bubble_html = f"""
        <div style="
            background-color: {bg_color};
            color: {text_color};
            padding: 10px 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            width: fit-content;
            max-width: 60%;
        ">
            <b>{username}:</b><br/>
            {text}
    </div>
        """
        st.markdown(bubble_html, unsafe_allow_html=True)

    # =============== INITIAL GREETINGS FROM 2 GROUP MEMBERS =============
    if len(st.session_state['messages']) == 0:
        # Add the introduction from "Ellie"
        st.session_state['messages'].append({
            "user": "Ellie",
            "text": st.session_state['introduction']
        })
        
        # "Gemini" -> pick 2 random from support group, generate greetings
        if st.session_state['support_group'] is not None:
            group_usernames = st.session_state['support_group']['USERNAME'].tolist()
            if len(group_usernames) > 2:
                random_two = random.sample(group_usernames, 2)
            else:
                random_two = group_usernames

            for g_user in random_two:
                # Generate a short greeting
                bio_user = example_data[example_data["USERNAME"]==g_user]["BIO"]

                greeting_prompt = f"You are pretending to be {g_user} and writing a short greeting an online mental health group for the first time. this is their bio {bio_user}. Keep it sensitive and light but friendly."
                greet_text = model_bio.generate_content(greeting_prompt).text
                st.session_state['messages'].append({
                    "user": g_user,
                    "text": greet_text
                })
                time.sleep(3)

    # ========== RENDER MESSAGES SO FAR ==========
    st.write("### Messages:")
    for msg in st.session_state['messages']:
        render_message_bubble(msg["user"], msg["text"])
        time.sleep(2)

    st.divider()

    # ========== INPUT FOR NEW MESSAGE ============
    new_message = st.text_input("Write your message here:")
    if st.button("Send"):
        if new_message.strip():
            # Add user message
            st.session_state['messages'].append({
                "user": st.session_state['user_name'],
                "text": new_message
            })
            # Once user sends a message for the first time, Ellie suggests a topic:
            # We'll do this only once or any time you want. Below is "only once."
            if not st.session_state['ellie_already_suggested_topic']:
                # Compose the entire conversation so far:
                conversation_so_far = "\n".join([
                    f"{m['user']}: {m['text']}" for m in st.session_state['messages']
                ])
                topic_prompt = f"""
                You are Ellie, the friendly and personable online mental health mediator mediator. Based on the conversation so far:
                {conversation_so_far}

                Please suggest a short conversation topic for the group to discuss.
                """
                topic_text = model_bio.generate_content(topic_prompt).text
                st.session_state['messages'].append({
                    "user": "Ellie",
                    "text": topic_text
                })
                st.session_state['ellie_already_suggested_topic'] = True

            st.rerun()
        else:
            st.warning("Message cannot be empty.")

##########################
# 7) PAGE NAVIGATION     #
##########################
page = st.session_state['page']

if page == "Sign-Up Page":
    sign_up_page()
elif page == "Loading Page":
    loading_page()
elif page == "Welcome Screen":
    welcome_page()
elif page == "Group Messaging Board":
    group_messaging_board()
