import streamlit as st
import time
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances
import google.generativeai as genai
import random
import os

GOOGLE_API_KEY = YOUR_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)
model_bio = genai.GenerativeModel('gemini-1.5-flash')


# Example dataset
example_data = pd.read_csv('Dataset/synthetic_user_data.csv')

# Placeholder for embedding generation (replace this with an actual embedding model)
def generate_embedding(bio):
    # Dummy embedding: convert bio to vector of word counts
    print(bio)
    EMBEDDING = genai.embed_content(model="models/text-embedding-004",
                                    content=bio)
    return EMBEDDING['embedding']





# Placeholder for content generation (replace with an actual language model)
def generate_content(prompt):

    return 

# Find the 6 nearest neighbors based on bio embeddings
def find_nearest_neighbors(user_bio, dataset, n_neighbors=6):
    # Generate embedding for the user's bio
    user_embedding = generate_embedding(user_bio)
    
    # Generate embeddings for the dataset
    dataset_embeddings = np.vstack(dataset['BIO'].apply(generate_embedding).values)
    
    # Compute distances (cosine distances)
    distances = cosine_distances([user_embedding], dataset_embeddings).flatten()
    
    # Find the indices of the nearest neighbors
    nearest_indices = distances.argsort()[:n_neighbors]
    return dataset.iloc[nearest_indices]

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = "Sign-Up Page"
if 'support_group' not in st.session_state:
    st.session_state['support_group'] = None
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'introduction' not in st.session_state:
    st.session_state['introduction'] = None

# Navigation logic
def navigate(page_name):
    st.session_state['page'] = page_name

# Pages
if st.session_state['page'] == "Sign-Up Page":
    st.title("Sign-Up for Your Support Network")
    
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=10, max_value=100, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    bio = st.text_area("Write a brief bio about yourself")
    
    if st.button("Submit"):
        if bio.strip():
            # Find nearest neighbors in the dataset
            st.session_state['support_group'] = find_nearest_neighbors(bio, example_data)
            
            # Generate personalized introduction
            combined_bio_prompt = "\n".join(st.session_state['support_group']['BIO'].astype(str))
            combined_users = "\n".join(st.session_state['support_group']['USERNAME'][1:].astype(str))
            introduction_prompt = f"Your name is Ellie and you are mediating a mental health support group.\
                                    Write a brief summary introductory message to bring the group together using the following self-written bios.\
                                    {combined_bio_prompt}"
            st.session_state['introduction'] = model_bio.generate_content(introduction_prompt).text
            
            # Add introduction to messages
            st.session_state['messages'].append(st.session_state['introduction'])
            
            navigate("Welcome Screen")
        else:
            st.warning("Please fill out the bio field.")

elif st.session_state['page'] == "Welcome Screen":
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
    time.sleep(5)
    navigate("Group Messaging Board")
    st.rerun()

elif st.session_state['page'] == "Group Messaging Board":
    st.title("Group Messaging Board")
    
    # Display group members
    st.subheader("Your Support Group:")
    for user in st.session_state['support_group']['USERNAME']:
        st.write(f"- {user}")
    
    st.divider()
    
    # Display messages
    st.write("### Messages:")
    for msg in st.session_state['messages']:
        st.write(f"- {msg}")
    
    # Input for new message
    new_message = st.text_input("Write your message:")
    if st.button("Send"):
        if new_message.strip():
            st.session_state['messages'].append(new_message)
        else:
            st.warning("Message cannot be empty.")


# import streamlit as st
# import time

# import google.generativeai as genai
# import random
# import pandas as pd 
# import os
# from tqdm import tqdm as tqdm
# import numpy as np


# dataset = pd.read_csv("Dataset/synthetic_user_data.csv")



# # Placeholder for embedding and support group selection
# def process_bio(bio):
#     time.sleep(2)  # Simulate processing time
#     return [f"User {i}" for i in range(1, 6)]  # Dummy support group

# # LLM mediator introduction
# def mediator_introduction():
#     return "Hello everyone! Welcome to your support group. I'm here to help facilitate the conversation. Feel free to introduce yourselves!"




# # Initialize session state for persistent app state
# if 'page' not in st.session_state:
#     st.session_state['page'] = "Sign-Up Page"
# if 'messages' not in st.session_state:
#     st.session_state['messages'] = [mediator_introduction()]
# if 'processing_done' not in st.session_state:
#     st.session_state['processing_done'] = False

# # Function to navigate to a different page
# def navigate(page_name):
#     st.session_state['page'] = page_name

# # Navigation logic
# if st.session_state['page'] == "Sign-Up Page":
#     st.title("Sign-Up for Your Support Network with SafeCircles")
    
#     # User input fields
#     name = st.text_input("Name")
#     age = st.number_input("Age", min_value=18, max_value=100, step=1)
#     gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
#     bio = st.text_area("Write a brief bio about yourself")
    
#     # Submit button
#     if st.button("Submit"):
#         if bio.strip():
#             st.session_state['user_bio'] = bio
#             st.session_state['support_group'] = process_bio(bio)
#             st.session_state['processing_done'] = False  # Reset processing state
#             navigate("Loading Page")
#         else:
#             st.warning("Please fill out the bio field.")

# elif st.session_state['page'] == "Loading Page":
#     st.title("Finding Your Support Group...")
#     st.write("We are processing your information to find the best match.")

#     # Embed animation
#     animation_html = """
#     <html>
#     <head>
#         <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js"></script>
#     </head>
#     <body>
#         <script>
#             let points = [];
#             let edges = [];
#             let settled = false;
#             let maxAge = 100;  // Maximum age for unstable edges

#             function setup() {
#                 createCanvas(600, 400);
#                 for (let i = 0; i < 100; i++) {
#                     points.push({
#                         x: random(width),
#                         y: random(height),
#                         vx: random(-1.5, 1.5),
#                         vy: random(-1.5, 1.5)
#                     });
#                 }
#                 for (let i = 0; i < 200; i++) {
#                     edges.push({
#                         start: int(random(points.length)),
#                         end: int(random(points.length)),
#                         age: random(maxAge),
#                         stable: random(1) < 0.2
#                     });
#                 }
#             }

#             function draw() {
#                 background(30);
#                 strokeWeight(2);
#                 for (let edge of edges) {
#                     let p1 = points[edge.start];
#                     let p2 = points[edge.end];
#                     if (edge.age > 0 || edge.stable) {
#                         stroke(edge.stable ? color(0, 255, 0, 150) : color(200, 150));
#                         line(p1.x, p1.y, p2.x, p2.y);
#                         edge.age -= 1;
#                     }
#                 }
#                 edges = edges.filter(edge => edge.age > 0 || edge.stable);
#                 if (frameCount % 10 === 0 && !settled) {
#                     edges.push({
#                         start: int(random(points.length)),
#                         end: int(random(points.length)),
#                         age: random(maxAge),
#                         stable: random(1) < 0.2
#                     });
#                 }
#                 noStroke();
#                 fill(255, 100, 100);
#                 for (let p of points) {
#                     ellipse(p.x, p.y, 10, 10);
#                     if (!settled) {
#                         p.x += p.vx;
#                         p.y += p.vy;
#                         p.vx *= 0.99;
#                         p.vy *= 0.99;
#                         if (p.x < 0 || p.x > width) p.vx *= -1;
#                         if (p.y < 0 || p.y > height) p.vy *= -1;
#                     }
#                 }
#                 if (!settled && frameCount > 300) {
#                     settled = true;
#                     for (let p of points) {
#                         p.vx = 0;
#                         p.vy = 0;
#                     }
#                 }
#             }
#         </script>
#     </body>
#     </html>
#     """
#     st.components.v1.html(animation_html, height=400)

#     if not st.session_state['processing_done']:
#         time.sleep(5)  # Simulate embedding computation
#         st.session_state['processing_done'] = True
#         navigate("Welcome Screen")
#     st.rerun()

# elif st.session_state['page'] == "Welcome Screen":
#     st.title("Welcome!")
#     fade_in_html = """
#     <html>
#     <head>
#         <style>
#             body {
#                 background-color: #1e1e1e;
#                 color: white;
#                 font-family: Arial, sans-serif;
#                 text-align: center;
#                 margin-top: 150px;
#             }
#             .fade-in {
#                 opacity: 0;
#                 animation: fadeIn 3s forwards;
#             }
#             @keyframes fadeIn {
#                 from { opacity: 0; }
#                 to { opacity: 1; }
#             }
#         </style>
#     </head>
#     <body>
#         <h1 class="fade-in">We've found you a group.<br>Welcome to SafeCircle.</h1>
#     </body>
#     </html>
#     """
#     st.components.v1.html(fade_in_html, height=400)

#     # After a short delay, navigate to the group messaging board
#     time.sleep(5)
#     navigate("Group Messaging Board")
#     st.rerun()

# elif st.session_state['page'] == "Group Messaging Board":
#     st.title("Group Messaging Board")
    
#     # Display support group members
#     st.subheader("Your Support Group:")
#     for user in st.session_state['support_group']:
#         st.write(f"- {user}")
    
#     st.divider()
    
#     # Display existing messages
#     st.write("### Messages:")
#     for msg in st.session_state['messages']:
#         st.write(f"- {msg}")
    
#     # Input for new message
#     new_message = st.text_input("Write your message:")
#     if st.button("Send"):
#         if new_message.strip():
#             st.session_state['messages'].append(new_message)
#         else:
#             st.warning("Message cannot be empty.")


















# import streamlit as st
# import time

# # Placeholder for embedding and support group selection
# def process_bio(bio):
#     time.sleep(2)  # Simulate processing time
#     return [f"User {i}" for i in range(1, 6)]  # Dummy support group

# # LLM mediator introduction
# def mediator_introduction():
#     return "Hello everyone! Welcome to your support group. I'm here to help facilitate the conversation. Feel free to introduce yourselves!"

# # Initialize session state for persistent app state
# if 'page' not in st.session_state:
#     st.session_state['page'] = "Sign-Up Page"
# if 'messages' not in st.session_state:
#     st.session_state['messages'] = [mediator_introduction()]
# if 'processing_done' not in st.session_state:
#     st.session_state['processing_done'] = False

# # Function to navigate to a different page
# def navigate(page_name):
#     st.session_state['page'] = page_name

# # Navigation logic
# if st.session_state['page'] == "Sign-Up Page":
#     st.title("Sign-Up for Your Support Network")
    
#     # User input fields
#     name = st.text_input("Name")
#     age = st.number_input("Age", min_value=10, max_value=100, step=1)
#     gender = st.selectbox("Gender", ["Male", "Female", "Other"])
#     bio = st.text_area("Write a brief bio about yourself")
    
#     # Submit button
#     if st.button("Submit"):
#         if bio.strip():
#             st.session_state['user_bio'] = bio
#             st.session_state['support_group'] = process_bio(bio)
#             st.session_state['processing_done'] = False  # Reset processing state
#             navigate("Loading Page")
#         else:
#             st.warning("Please fill out the bio field.")

# elif st.session_state['page'] == "Loading Page":
#     st.title("Finding Your Support Group...")
#     st.write("We are processing your information to find the best match.")

#     # Embed enhanced animation
#     animation_html = """
#     <html>
#     <head>
#         <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js"></script>
#     </head>
#     <body>
#         <script>
#             let points = [];
#             let edges = [];
#             let settled = false;
#             let maxAge = 100;  // Maximum age for unstable edges

#             function setup() {
#                 createCanvas(600, 400);

#                 // Initialize random points
#                 for (let i = 0; i < 100; i++) {
#                     points.push({
#                         x: random(width),
#                         y: random(height),
#                         vx: random(-1.5, 1.5),
#                         vy: random(-1.5, 1.5)
#                     });
#                 }
                
#                 // Initialize edges with random ages
#                 for (let i = 0; i < 200; i++) {
#                     edges.push({
#                         start: int(random(points.length)),
#                         end: int(random(points.length)),
#                         age: random(maxAge),  // Random starting age
#                         stable: random(1) < 0.2  // 20% of edges are stable
#                     });
#                 }
#             }

#             function draw() {
#                 background(30);

#                 // Draw edges
#                 strokeWeight(2);
#                 for (let edge of edges) {
#                     let p1 = points[edge.start];
#                     let p2 = points[edge.end];
#                     if (edge.age > 0 || edge.stable) {
#                         stroke(edge.stable ? color(0, 255, 0, 150) : color(200, 150));  // Stable edges are green
#                         line(p1.x, p1.y, p2.x, p2.y);
#                         edge.age -= 1;  // Age decreases for unstable edges
#                     }
#                 }

#                 // Remove old edges and add new ones dynamically
#                 edges = edges.filter(edge => edge.age > 0 || edge.stable);
#                 if (frameCount % 10 === 0 && !settled) {  // New edges every 10 frames
#                     edges.push({
#                         start: int(random(points.length)),
#                         end: int(random(points.length)),
#                         age: random(maxAge),  // New edges with random age
#                         stable: random(1) < 0.2  // 20% chance to be stable
#                     });
#                 }

#                 // Draw points and update their positions
#                 noStroke();
#                 fill(255, 100, 100);
#                 for (let p of points) {
#                     ellipse(p.x, p.y, 10, 10);

#                     if (!settled) {
#                         p.x += p.vx;
#                         p.y += p.vy;

#                         // Slow down motion gradually
#                         p.vx *= 0.99;
#                         p.vy *= 0.99;

#                         // Reverse velocity if hitting the edges
#                         if (p.x < 0 || p.x > width) p.vx *= -1;
#                         if (p.y < 0 || p.y > height) p.vy *= -1;
#                     }
#                 }

#                 // Gradually settle into a stable configuration
#                 if (!settled && frameCount > 300) {
#                     settled = true;
#                     for (let p of points) {
#                         p.vx = 0;
#                         p.vy = 0;
#                     }
#                 }
#             }
#         </script>
#     </body>
#     </html>
#     """
#     st.components.v1.html(animation_html, height=400)

#     # Simulate processing and navigate to the next page
#     if not st.session_state['processing_done']:
#         time.sleep(5)  # Simulate embedding computation
#         st.session_state['processing_done'] = True
#         navigate("Group Messaging Board")
#     st.rerun()

# elif st.session_state['page'] == "Group Messaging Board":
#     st.title("Group Messaging Board")
    
#     # Display support group members
#     st.subheader("Your Support Group:")
#     for user in st.session_state['support_group']:
#         st.write(f"- {user}")
    
#     st.divider()
    
#     # Display existing messages
#     st.write("### Messages:")
#     for msg in st.session_state['messages']:
#         st.write(f"- {msg}")
    
#     # Input for new message
#     new_message = st.text_input("Write your message:")
#     if st.button("Send"):
#         if new_message.strip():
#             st.session_state['messages'].append(new_message)
#         else:
#             st.warning("Message cannot be empty.")


# import streamlit as st
# import time

# # Placeholder for embedding and support group selection
# def process_bio(bio):
#     time.sleep(2)  # Simulate processing time
#     return [f"User {i}" for i in range(1, 6)]  # Dummy support group

# # LLM mediator introduction
# def mediator_introduction():
#     return "Hello everyone! Welcome to your support group. I'm here to help facilitate the conversation. Feel free to introduce yourselves!"

# # Initialize session state for persistent app state
# if 'page' not in st.session_state:
#     st.session_state['page'] = "Sign-Up Page"
# if 'messages' not in st.session_state:
#     st.session_state['messages'] = [mediator_introduction()]
# if 'processing_done' not in st.session_state:
#     st.session_state['processing_done'] = False

# # Function to navigate to a different page
# def navigate(page_name):
#     st.session_state['page'] = page_name

# # Navigation logic
# if st.session_state['page'] == "Sign-Up Page":
#     st.title("Sign-Up for Your Support Network")
    
#     # User input fields
#     name = st.text_input("Name")
#     age = st.number_input("Age", min_value=10, max_value=100, step=1)
#     gender = st.selectbox("Gender", ["Male", "Female", "Other"])
#     bio = st.text_area("Write a brief bio about yourself")
    
#     # Submit button
#     if st.button("Submit"):
#         if bio.strip():
#             st.session_state['user_bio'] = bio
#             st.session_state['support_group'] = process_bio(bio)
#             st.session_state['processing_done'] = False  # Reset processing state
#             navigate("Loading Page")
#         else:
#             st.warning("Please fill out the bio field.")

# elif st.session_state['page'] == "Loading Page":
#     st.title("Finding Your Support Group...")
#     st.write("We are processing your information to find the best match.")

#     # Embed cloud animation
#     animation_html = """
#     <html>
#     <head>
#         <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js"></script>
#     </head>
#     <body>
#         <script>
#             let points = [];
#             let edges = [];
#             let settled = false;

#             function setup() {
#                 createCanvas(600, 400);
#                 // Initialize random points
#                 for (let i = 0; i < 100; i++) {  // More points
#                     points.push({
#                         x: random(width),
#                         y: random(height),
#                         vx: random(-1, 1),
#                         vy: random(-1, 1)
#                     });
#                 }
#             }

#             function draw() {
#                 background(30);

#                 // Form and dissolve edges every 60 frames
#                 if (frameCount % 60 === 0 && !settled) {
#                     edges = [];
#                     for (let i = 0; i < points.length; i++) {
#                         for (let j = i + 1; j < points.length; j++) {
#                             if (random(1) < 0.005) { // Fewer connections
#                                 edges.push([i, j]);
#                             }
#                         }
#                     }
#                 }

#                 // Draw edges
#                 stroke(200, 150);
#                 strokeWeight(3);  // Thicker lines
#                 for (let edge of edges) {
#                     let p1 = points[edge[0]];
#                     let p2 = points[edge[1]];
#                     line(p1.x, p1.y, p2.x, p2.y);
#                 }

#                 // Draw points and update their positions
#                 noStroke();
#                 fill(255, 100, 100);
#                 for (let p of points) {
#                     ellipse(p.x, p.y, 10, 10);

#                     if (!settled) {
#                         p.x += p.vx;
#                         p.y += p.vy;

#                         // Slow down motion gradually
#                         p.vx *= 0.98;
#                         p.vy *= 0.98;

#                         // Reverse velocity if hitting the edges
#                         if (p.x < 0 || p.x > width) p.vx *= -1;
#                         if (p.y < 0 || p.y > height) p.vy *= -1;
#                     }
#                 }

#                 // Gradually settle into a stable configuration
#                 if (!settled && frameCount > 300) {
#                     settled = true;
#                     for (let p of points) {
#                         p.vx = 0;
#                         p.vy = 0;
#                     }
#                 }
#             }
#         </script>
#     </body>
#     </html>
#     """
#     st.components.v1.html(animation_html, height=400)

#     # Simulate processing and navigate to the next page
#     if not st.session_state['processing_done']:
#         time.sleep(5)  # Simulate embedding computation
#         st.session_state['processing_done'] = True
#         navigate("Group Messaging Board")
#     st.rerun()

# elif st.session_state['page'] == "Group Messaging Board":
#     st.title("Group Messaging Board")
    
#     # Display support group members
#     st.subheader("Your Support Group:")
#     for user in st.session_state['support_group']:
#         st.write(f"- {user}")
    
#     st.divider()
    
#     # Display existing messages
#     st.write("### Messages:")
#     for msg in st.session_state['messages']:
#         st.write(f"- {msg}")
    
#     # Input for new message
#     new_message = st.text_input("Write your message:")
#     if st.button("Send"):
#         if new_message.strip():
#             st.session_state['messages'].append(new_message)
#         else:
#             st.warning("Message cannot be empty.")



# import streamlit as st
# import time

# # Placeholder for embedding and support group selection
# def process_bio(bio):
#     time.sleep(2)  # Simulate processing time
#     return [f"User {i}" for i in range(1, 6)]  # Dummy support group

# # LLM mediator introduction
# def mediator_introduction():
#     return "Hello everyone! Welcome to your support group. I'm here to help facilitate the conversation. Feel free to introduce yourselves!"

# # Initialize session state for persistent app state
# if 'page' not in st.session_state:
#     st.session_state['page'] = "Sign-Up Page"
# if 'messages' not in st.session_state:
#     st.session_state['messages'] = [mediator_introduction()]
# if 'processing_done' not in st.session_state:
#     st.session_state['processing_done'] = False

# # Function to navigate to a different page
# def navigate(page_name):
#     st.session_state['page'] = page_name

# # Navigation logic
# if st.session_state['page'] == "Sign-Up Page":
#     st.title("Sign-Up for Your Support Network")
    
#     # User input fields
#     name = st.text_input("Name")
#     age = st.number_input("Age", min_value=10, max_value=100, step=1)
#     gender = st.selectbox("Gender", ["Male", "Female", "Other"])
#     bio = st.text_area("Write a brief bio about yourself")
    
#     # Submit button
#     if st.button("Submit"):
#         if bio.strip():
#             st.session_state['user_bio'] = bio
#             st.session_state['support_group'] = process_bio(bio)
#             st.session_state['processing_done'] = False  # Reset processing state
#             navigate("Loading Page")
#         else:
#             st.warning("Please fill out the bio field.")

# elif st.session_state['page'] == "Loading Page":
#     st.title("Finding Your Support Group...")
#     st.write("We are processing your information to find the best match.")

#     # Embed cloud animation
#     animation_html = """
#     <html>
#     <head>
#         <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js"></script>
#     </head>
#     <body>
#         <script>
#             let points = [];
#             let edges = [];
#             let settled = false;

#             function setup() {
#                 createCanvas(600, 400);
#                 // Initialize random points
#                 for (let i = 0; i < 50; i++) {
#                     points.push({
#                         x: random(width),
#                         y: random(height),
#                         vx: random(-2, 2),
#                         vy: random(-2, 2)
#                     });
#                 }
#             }

#             function draw() {
#                 background(0);
#                 stroke(200, 100);
#                 strokeWeight(1);

#                 // Form and dissolve edges randomly
#                 if (!settled) {
#                     edges = [];
#                     for (let i = 0; i < points.length; i++) {
#                         for (let j = i + 1; j < points.length; j++) {
#                             if (random(1) < 0.02) { // Small chance of forming a connection
#                                 edges.push([i, j]);
#                             }
#                         }
#                     }
#                 }

#                 // Draw edges
#                 for (let edge of edges) {
#                     let p1 = points[edge[0]];
#                     let p2 = points[edge[1]];
#                     line(p1.x, p1.y, p2.x, p2.y);
#                 }

#                 // Draw points and update their positions
#                 noStroke();
#                 fill(255, 100, 100);
#                 for (let p of points) {
#                     ellipse(p.x, p.y, 8, 8);

#                     if (!settled) {
#                         p.x += p.vx;
#                         p.y += p.vy;

#                         // Slow down motion gradually
#                         p.vx *= 0.99;
#                         p.vy *= 0.99;

#                         // Reverse velocity if hitting the edges
#                         if (p.x < 0 || p.x > width) p.vx *= -1;
#                         if (p.y < 0 || p.y > height) p.vy *= -1;
#                     }
#                 }

#                 // Gradually settle into a stable configuration
#                 if (!settled && frameCount > 300) {
#                     settled = true;
#                     for (let p of points) {
#                         p.vx = 0;
#                         p.vy = 0;
#                     }
#                 }
#             }
#         </script>
#     </body>
#     </html>
#     """
#     st.components.v1.html(animation_html, height=400)

#     # Simulate processing and navigate to the next page
#     if not st.session_state['processing_done']:
#         time.sleep(5)  # Simulate embedding computation
#         st.session_state['processing_done'] = True
#         navigate("Group Messaging Board")
#     st.experimental_rerun()

# elif st.session_state['page'] == "Group Messaging Board":
#     st.title("Group Messaging Board")
    
#     # Display support group members
#     st.subheader("Your Support Group:")
#     for user in st.session_state['support_group']:
#         st.write(f"- {user}")
    
#     st.divider()
    
#     # Display existing messages
#     st.write("### Messages:")
#     for msg in st.session_state['messages']:
#         st.write(f"- {msg}")
    
#     # Input for new message
#     new_message = st.text_input("Write your message:")
#     if st.button("Send"):
#         if new_message.strip():
#             st.session_state['messages'].append(new_message)
#         else:
#             st.warning("Message cannot be empty.")



# import streamlit as st
# import time

# # Placeholder for embedding and support group selection
# def process_bio(bio):
#     time.sleep(2)  # Simulate processing time
#     return [f"User {i}" for i in range(1, 6)]  # Dummy support group

# # LLM mediator introduction
# def mediator_introduction():
#     return "Hello everyone! Welcome to your support group. I'm here to help facilitate the conversation. Feel free to introduce yourselves!"

# # Initialize session state for persistent app state
# if 'page' not in st.session_state:
#     st.session_state['page'] = "Sign-Up Page"
# if 'messages' not in st.session_state:
#     st.session_state['messages'] = [mediator_introduction()]
# if 'processing_done' not in st.session_state:
#     st.session_state['processing_done'] = False

# # Function to navigate to a different page
# def navigate(page_name):
#     st.session_state['page'] = page_name

# # Navigation logic
# if st.session_state['page'] == "Sign-Up Page":
#     st.title("Sign-Up for Your Support Network")
    
#     # User input fields
#     name = st.text_input("Name")
#     age = st.number_input("Age", min_value=10, max_value=100, step=1)
#     gender = st.selectbox("Gender", ["Male", "Female", "Other"])
#     bio = st.text_area("Write a brief bio about yourself")
    
#     # Submit button
#     if st.button("Submit"):
#         if bio.strip():
#             st.session_state['user_bio'] = bio
#             st.session_state['support_group'] = process_bio(bio)
#             st.session_state['processing_done'] = False  # Reset processing state
#             navigate("Loading Page")
#         else:
#             st.warning("Please fill out the bio field.")

# elif st.session_state['page'] == "Loading Page":
#     st.title("Finding Your Support Group...")
#     st.write("We are processing your information to find the best match.")

#     # Embed ball-and-stick animation
#     animation_html = """
#     <html>
#     <head>
#         <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js"></script>
#     </head>
#     <body>
#         <script>
#             let nodes = [];
#             let edges = [];

#             function setup() {
#                 createCanvas(400, 400);
#                 for (let i = 0; i < 10; i++) {
#                     nodes.push(createVector(random(width), random(height)));
#                 }
#                 for (let i = 0; i < 15; i++) {
#                     edges.push([
#                         int(random(nodes.length)),
#                         int(random(nodes.length))
#                     ]);
#                 }
#             }

#             function draw() {
#                 background(30);
#                 stroke(200);
#                 strokeWeight(2);
#                 for (let edge of edges) {
#                     let nodeA = nodes[edge[0]];
#                     let nodeB = nodes[edge[1]];
#                     line(nodeA.x, nodeA.y, nodeB.x, nodeB.y);
#                 }
#                 noStroke();
#                 fill(255, 100, 100);
#                 for (let node of nodes) {
#                     ellipse(node.x, node.y, 10, 10);
#                     node.x += random(-1, 1);
#                     node.y += random(-1, 1);
#                 }
#             }
#         </script>
#     </body>
#     </html>
#     """
#     st.components.v1.html(animation_html, height=400)

#     # Simulate processing and navigate to the next page
#     if not st.session_state['processing_done']:
#         time.sleep(5)  # Simulate embedding computation
#         st.session_state['processing_done'] = True
#         navigate("Group Messaging Board")
#     st.experimental_rerun()

# elif st.session_state['page'] == "Group Messaging Board":
#     st.title("Group Messaging Board")
    
#     # Display support group members
#     st.subheader("Your Support Group:")
#     for user in st.session_state['support_group']:
#         st.write(f"- {user}")
    
#     st.divider()
    
#     # Display existing messages
#     st.write("### Messages:")
#     for msg in st.session_state['messages']:
#         st.write(f"- {msg}")
    
#     # Input for new message
#     new_message = st.text_input("Write your message:")
#     if st.button("Send"):
#         if new_message.strip():
#             st.session_state['messages'].append(new_message)
#         else:
#             st.warning("Message cannot be empty.")



# import streamlit as st
# import time
# import pandas
# import numpy
# import google.generativeai as genai

# user_data = pd.read_csv("Dataset/synthetic_user_data.csv")

# GOOGLE_API_KEY ="AIzaSyCFdA1B8ZUaVUb1TjrVyzvycRCrcyKy2d4"
# genai.configure(api_key=GOOGLE_API_KEY)
# model_bio = genai.GenerativeModel('gemini-1.5-flash')

# def get_network(user_data)


# # Placeholder for embedding and support group selection
# def process_bio(bio):
#     time.sleep(2)  # Simulate processing time
#     return [f"User {i}" for i in range(1, 6)]  # Dummy support group

# # LLM mediator introduction
# def mediator_introduction():
#     return "Hello everyone! Welcome to your support group. I'm here to help facilitate the conversation. Feel free to introduce yourselves!"

# # Initialize session state for persistent app state
# if 'page' not in st.session_state:
#     st.session_state['page'] = "Sign-Up Page"
# if 'messages' not in st.session_state:
#     st.session_state['messages'] = [mediator_introduction()]
# if 'processing_done' not in st.session_state:
#     st.session_state['processing_done'] = False

# # Function to navigate to a different page
# def navigate(page_name):
#     st.session_state['page'] = page_name

# # Navigation logic
# if st.session_state['page'] == "Sign-Up Page":
#     st.title("Sign-Up for Your Support Network")
    
#     # User input fields
#     name = st.text_input("Name")
#     age = st.number_input("Age", min_value=18, max_value=110, step=1)
#     gender = st.selectbox("Gender", ["Male", "Female", "Non-Binary", "Prefer not to say"])
#     bio = st.text_area("Write a brief bio about yourself")
    
#     # Submit button
#     if st.button("Submit"):
#         if bio.strip():
#             st.session_state['user_bio'] = bio
#             st.session_state['support_group'] = process_bio(bio)
#             st.session_state['processing_done'] = False  # Reset processing state
#             navigate("Loading Page")
#         else:
#             st.warning("Please fill out the bio field.")

# elif st.session_state['page'] == "Loading Page":
#     st.title("Finding Your Support Group...")
#     st.write("We are processing your information to find the best match.")

#     with st.spinner("Processing..."):
#         if not st.session_state['processing_done']:
#             time.sleep(3)  # Simulate embedding computation
#             st.session_state['processing_done'] = True
#             navigate("Group Messaging Board")  # Navigate once processing is complete
#     st.rerun()  # Force the app to refresh after updating the state

# elif st.session_state['page'] == "Group Messaging Board":
#     st.title("Group Messaging Board")
    
#     # Display support group members
#     st.subheader("Your Support Group:")
#     for user in st.session_state['support_group']:
#         st.write(f"- {user}")
    
#     st.divider()
    
#     # Display existing messages
#     st.write("### Messages:")
#     for msg in st.session_state['messages']:
#         st.write(f"- {msg}")
    
#     # Input for new message
#     new_message = st.text_input("Write your message:")
#     if st.button("Send"):
#         if new_message.strip():
#             st.session_state['messages'].append(new_message)
#         else:
#             st.warning("Message cannot be empty.")




# import streamlit as st
# import time

# # Placeholder for embedding and support group selection
# def process_bio(bio):
#     time.sleep(2)  # Simulate processing time
#     return [f"User {i}" for i in range(1, 6)]  # Dummy support group

# # LLM mediator introduction
# def mediator_introduction():
#     return "Hello everyone! Welcome to your support group. I'm here to help facilitate the conversation. Feel free to introduce yourselves!"

# # Initialize session state for persistent app state
# if 'page' not in st.session_state:
#     st.session_state['page'] = "Sign-Up Page"
# if 'messages' not in st.session_state:
#     st.session_state['messages'] = [mediator_introduction()]

# # Function to navigate to a different page
# def navigate(page_name):
#     st.session_state['page'] = page_name

# # Navigation logic
# if st.session_state['page'] == "Sign-Up Page":
#     st.title("Sign-Up for Your Support Network")
    
#     # User input fields
#     name = st.text_input("Name")
#     age = st.number_input("Age", min_value=10, max_value=100, step=1)
#     gender = st.selectbox("Gender", ["Male", "Female", "Other"])
#     bio = st.text_area("Write a brief bio about yourself")
    
#     # Submit button
#     if st.button("Submit"):
#         if bio.strip():
#             st.session_state['user_bio'] = bio
#             st.session_state['support_group'] = process_bio(bio)
#             navigate("Loading Page")
#         else:
#             st.warning("Please fill out the bio field.")

# elif st.session_state['page'] == "Loading Page":
#     st.title("Finding Your Support Group...")
#     st.write("We are processing your information to find the best match.")
#     with st.spinner("Processing..."):
#         time.sleep(3)  # Simulate time for embedding and group matching
#     navigate("Group Messaging Board")

# elif st.session_state['page'] == "Group Messaging Board":
#     st.title("Group Messaging Board")
    
#     # Display support group members
#     st.subheader("Your Support Group:")
#     for user in st.session_state['support_group']:
#         st.write(f"- {user}")
    
#     st.divider()
    
#     # Display existing messages
#     st.write("### Messages:")
#     for msg in st.session_state['messages']:
#         st.write(f"- {msg}")
    
#     # Input for new message
#     new_message = st.text_input("Write your message:")
#     if st.button("Send"):
#         if new_message.strip():
#             st.session_state['messages'].append(new_message)
#             st.experimental_set_query_params(reload="true")
#         else:
#             st.warning("Message cannot be empty.")

# import streamlit as st
# import time
# import random

# # Placeholder for embedding and support group selection
# def process_bio(bio):
#     time.sleep(2)  # Simulating processing time
#     return [f"User {i}" for i in range(1, 6)]  # Dummy support group

# # LLM mediator introduction
# def mediator_introduction():
#     return "Hello everyone! Welcome to your support group. I'm here to help facilitate the conversation. Feel free to introduce yourselves!"

# # Initialize session state for group messages
# if 'messages' not in st.session_state:
#     st.session_state['messages'] = [mediator_introduction()]

# # App layout with different pages
# st.sidebar.title("Navigation")
# page = st.sidebar.radio("Go to", ["Sign-Up Page", "Loading Page", "Group Messaging Board"])

# if page == "Sign-Up Page":
#     st.title("Welcome to ")
#     st.title("Sign-Up for Your Support Network")
#     # User input fields
#     name = st.text_input("Name")
#     age = st.number_input("Age", min_value=10, max_value=100, step=1)
#     gender = st.selectbox("Gender", ["Male", "Female", "Other"])
#     bio = st.text_area("Write a brief bio about yourself")
    
#     # Submit button
#     if st.button("Submit"):
#         if bio.strip():
#             st.session_state['user_bio'] = bio
#             st.session_state['support_group'] = process_bio(bio)
#             st.session_state['page'] = "Loading Page"
#             st.experimental_rerun()
#         else:
#             st.warning("Please fill out the bio field.")
            
# elif page == "Loading Page":
#     st.title("Finding Your Support Group...")
#     st.write("We are processing your information to find the best match.")
#     st.spinner("Processing...")
#     time.sleep(3)  # Simulate time for embedding and group matching
    
#     # Redirect to messaging board
#     st.session_state['page'] = "Group Messaging Board"
#     st.experimental_rerun()

# elif page == "Group Messaging Board":
#     st.title("Group Messaging Board")
    
#     # Display support group members
#     st.subheader("Your Support Group:")
#     for user in st.session_state['support_group']:
#         st.write(f"- {user}")
    
#     st.divider()
    
#     # Display existing messages
#     st.write("### Messages:")
#     for msg in st.session_state['messages']:
#         st.write(f"- {msg}")
    
#     # Input for new message
#     new_message = st.text_input("Write your message:")
#     if st.button("Send"):
#         if new_message.strip():
#             st.session_state['messages'].append(new_message)
#             st.experimental_rerun()
#         else:
#             st.warning("Message cannot be empty.")
