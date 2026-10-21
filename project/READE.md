# FAMILY FOREST
#### Video Demo:  <URL HERE>
#### Description:

The motivation behind Family Forest:
Most genealogy software are too rigit, hierarchical and unsuited for modern complex families like my own. With Family Forest I wanted to create something that felt more like a garden than a spreadsheet. I wanted a tool that could map the organic, messy, and beautiful ways we connect with others, including those who aren't "traditionally" family, like lifelong friends or beloved pets.

In this project, I moved away from the standard "Family Tree" hierarchy and instead implemented a force-directed graph. This means the connections are dynamic; as you add people, the "forest" grows, shifts, and finds its own equilibrium. It’s a visualization of a personal ecosystem where the people most central to your life literally anchor the visualization.

The architecture:
I spent a significant amount of time ensuring that the backend was lean and the frontend was expressive. Here is a breakdown of the files I wrote and how they interact to bring the forest to life:

1. app.py
This is the heart of my application. Built using Flask, it manages the logic that bridges the database with the user interface.

Dynamic Inference: One of the features I’m most proud of is the sibling detection logic. Instead of forcing a user to manually link every brother and sister—which becomes tedious in large families—I wrote a script using itertools.combinations. It scans the database for people sharing the same parents and automatically creates "sibling" edges. This ensures the data remains clean while the visual remains complete.

Security and Session Management: I implemented full session management and password hashing using werkzeug.security. Even though this is a personal project, I treated user data with the respect it deserves, ensuring that each user can only see and edit their own private forest.

The Data Bridge: I designed the /graph-data route to act as a custom API. It queries my SQLite tables and transforms them into a structured JSON format that the visualization engine can understand, separating nodes (people) from edges (relationships).

2. graph.js (The Artist)
If app.py is the brain, graph.js is the soul of the project. Using the Vis.js library as a foundation, I wrote extensive custom logic to handle the aesthetics:

The Botanical Metaphor: I didn't want generic circles. I wrote functions like leafSVG and logSVG to programmatically generate icons. The user (the root) is represented by a "Log" icon, while others appear as "Leaves."

Degree-Based Scaling: I implemented a "Branch Strength" algorithm. The script calculates how many connections a person has (their "degree") and uses that to scale their size. This makes influential family matriarchs or patriarchs appear larger and more "grounded" in the visualization.

Physics Tuning: I spent hours tweaking the forceAtlas2Based physics solver. I wanted the nodes to feel like they had weight, preventing the "clumping" that often ruins graph visualizations.

3. familyforest.db (The Roots)
For the database, I chose SQLite. I designed a schema that prioritizes flexibility over rigid hierarchies:

The People Table: Stores names, birthdates, and personal notes. I made sure to handle "Unknown" values gracefully, so the graph doesn't break if a user doesn't have a full history for an ancestor.

The Relationships Table: This is a polymorphic table. Instead of having separate tables for "Parents" or "Marriages," I used a single junction table with a relationship_type column. This allows me to support everything from biological parents to "Ex-Spouses" and "Pets" without changing the database structure.

4. helpers.py (The Sentinel)
I kept this file focused on utility. It contains the login_required decorator, which I used to wrap my routes. This ensures a clean separation of concerns: app.py handles the "what," and helpers.py handles the "who."

Design Choices and Personal Debates
The "Sibling" Dilemma: UX vs. Database Cleanliness
During development, I had a major debate with myself: Should I let users manually draw a line between siblings? Initially, I did. But I realized that if a parent has five children, the user has to draw ten separate lines to connect all the siblings to each other. It felt like "busy work." I decided to delete that manual feature and move the logic to the backend. Now, the software "understands" who is a sibling based on shared parentage. It was significantly harder to code the logic to prevent duplicate lines and ensure the math was correct, but it makes the user experience much more fluid and professional.

Aesthetics over Standard Icons
I debated using standard FontAwesome icons for people, but they felt too "corporate" and cold. I chose instead to write custom SVG code inside graph.js. By using SVG paths, I could control the exact shade of "Forest Green" and the "Wood Brown" of the logs. It gives the project a handcrafted, artisanal feel that matches the personal nature of family history. I also used unique colors for lines—pink for spouses and orange for pets—to help the eye categorize the network at a glance.

The Decision for a Graph vs. a Tree
Traditional family trees struggle with "cycles"—for example, if two brothers in one family marry two sisters from another family. A standard tree structure usually crashes or duplicates nodes in these scenarios. By choosing a graph-based approach, I solved this problem entirely. The nodes simply find their place in space regardless of how complex the web of relationships becomes. This choice was about future-proofing the project for modern, non-linear family structures.

Technical Challenges Overcome
The biggest challenge was the Physics of Relationships. In early versions, the "Pets" would fly off to the edge of the screen, or "Spouses" would overlap so much you couldn't read their names. I had to learn how to manipulate "Spring Length" and "Gravitational Constant" within the JavaScript engine. I eventually settled on a system where different relationship types have different "tension" levels—keeping spouses close and parents/children at a stable distance.

Reflection
Building Family Forest was a journey in balancing data integrity with visual storytelling. I’m proud of how I took a complex data structure (a non-linear graph) and made it accessible through a simple, inviting interface. It’s more than just a coding exercise to me; it’s a way to see the "forest" of our lives in a whole new light.

I hope you enjoy exploring your roots as much as I enjoyed coding them.
