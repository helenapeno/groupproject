from flask import Flask, render_template, redirect, request, session

app = Flask(__name__)
app.secret_key = "recipebooksecretkey"