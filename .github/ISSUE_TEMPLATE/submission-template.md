---
name: Hackathon Project Submission
about: Submit your project for the Global Agent Hackathon
title: "[Project Submission] Aza Man"
labels: submission
assignees: ''

---

## Project Title
Aza Man - AI-Powered Autonomous Financial Assistant

## Overview of the Idea
Aza Man is an AI-driven financial assistant designed to simplify personal finance management. It addresses the problem of financial overwhelm by providing intuitive tools for budgeting, expense tracking, and savings planning. The opportunity lies in empowering users—especially those with limited financial literacy—to make informed decisions through a user-friendly, AI-guided interface.

## Project Goal
The goal is to demonstrate a robust AI agent that autonomously assists users in managing their finances with precision and ease. Aza Man aims to showcase seamless integration of AI-driven insights, real-time expense tracking, and visual dashboards to promote financial discipline and goal achievement.

## How It Works
Aza Man operates as an interactive financial companion, leveraging AI to guide users through their financial journey:

* ### User Flow:

Users log in with a unique User ID (4-10 characters, ending with 2 digits, e.g., "odogwu19").
New users are prompted to set a username and create a budget (income, savings goal, currency).
Users interact via a chat interface, asking questions or logging expenses (e.g., "Log $50 for groceries").
The dashboard provides visual summaries of income, expenses, and savings progress.
Users can reset their session with a "RETURN TO BASE" option.


* ### Core Functionality:

Smart Budgeting: Allocates income into savings and expenses based on user-defined goals.
Expense Tracking: Logs and categorizes expenses, calculating totals in real-time.
Savings Goals: Tracks progress toward savings targets with visual indicators.
AI Chat: Provides financial advice and processes requests using natural language.
Dashboard Visualizations: Displays savings progress (gauge), expense distribution (pie chart), and trends (line chart).


* ### Multimodal Elements:

Text: Chat interface for user inputs and AI responses.
Visuals: Interactive dashboards with Plotly charts (gauge, pie, line).
Images: Custom logo and themed UI elements for enhanced aesthetics.



## Tools Used

Streamlit: For the web-based user interface.
LangChain/LangGraph: For AI agent workflows and tool integration.
Plotly: For interactive financial visualizations.
Python: Core programming language.
SQLite: For persistent state management.
Potential Additions: Exploring Agno for enhanced agent capabilities or Firecrawl for external data retrieval, pending hackathon resource details.

## UI Approach
The UI is a dark-themed, centered Streamlit application with custom CSS for a sleek, modern look. Key elements include:

* ### Sidebar Navigation: Options for Home, Chat, and Dashboard pages.
Chat Interface: Minimalist input field with a "Send" button, displaying user and AI messages in distinct styles.
Dashboard: Clean layout with metrics (income, expenses, savings) and interactive charts.
Responsive Design: Optimized for accessibility with hover effects and a red-accented color scheme.

* ### Visuals

Savings Progress Gauge: A Plotly gauge showing current savings vs. the goal.
Expense Distribution Pie Chart: Visualizes spending by category (e.g., groceries, utilities).
Expense Trends Line Chart: Tracks spending over time.
Mockup Description: The login page features a centered input for User ID, followed by a chat page with a red-bordered message area and a dashboard with tiled metrics and charts.

## Team Information

Team Lead: @chinonsoodiaka - Project Architect and Developer
Team Members: None (solo project)
Background/Experience: Experienced in AI development and web applications, with a focus on Python, LangChain, and data visualization. Passionate about creating impactful tools for everyday users.

## Prize Category

 Best use of Agno
 Best use of Firecrawl
 Best use of Mem0
 Best use of Graphlit
 Best use of Browser Use
 Best Overall Project

Demo Video Link


## Additional Notes
Aza Man is designed for scalability, with potential to integrate sponsor tools like Agno for advanced agent logic or Mem0 for conversation memory. The project emphasizes user empowerment through clear, actionable financial insights, making it a strong candidate for the hackathon's AI agent focus. Progress updates will be shared on X with #GlobalAgentHackathon to engage the community.
