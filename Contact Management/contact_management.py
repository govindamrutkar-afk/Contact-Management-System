from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = "contact-manager-internship-key"

# File for storing contacts
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contacts.json")


# Load contacts from JSON file
def load_contacts():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []
    return []


contacts = load_contacts()


# Save contacts to JSON file
def save_contacts():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4)


# Find a contact using its unique ID
def find_contact(contact_id):
    return next(
        (contact for contact in contacts
         if contact["id"] == contact_id),
        None
    )


# Display dashboard and contacts
@app.route("/")
def home():
    search = request.args.get("search", "").strip().lower()

    filtered_contacts = [
        contact for contact in contacts
        if search in contact["name"].lower()
        or search in contact["phone"].lower()
        or search in contact.get("email", "").lower()
    ]

    return render_template(
        "index.html",
        contacts=filtered_contacts,
        total_contacts=len(contacts),
        search=request.args.get("search", "")
    )


# Add a new contact
@app.route("/add", methods=["POST"])
def add_contact():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()

    if not name or not phone:
        flash("Name and phone number are required.", "error")
        return redirect(url_for("home"))

    duplicate = any(
        contact["name"].casefold() == name.casefold()
        for contact in contacts
    )

    if duplicate:
        flash("A contact with this name already exists.", "error")
        return redirect(url_for("home"))

    new_id = max(
        (contact["id"] for contact in contacts),
        default=0
    ) + 1

    contacts.append({
        "id": new_id,
        "name": name,
        "phone": phone,
        "email": email
    })

    save_contacts()
    flash("Contact added successfully!", "success")

    return redirect(url_for("home"))


# Edit an existing contact
@app.route("/edit/<int:contact_id>", methods=["GET", "POST"])
def edit_contact(contact_id):
    contact = find_contact(contact_id)

    if contact is None:
        flash("Contact not found.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not phone:
            flash("Name and phone number are required.", "error")
            return redirect(url_for("edit_contact", contact_id=contact_id))

        duplicate = any(
            item["id"] != contact_id
            and item["name"].casefold() == name.casefold()
            for item in contacts
        )

        if duplicate:
            flash("Another contact already uses this name.", "error")
            return redirect(url_for("edit_contact", contact_id=contact_id))

        contact["name"] = name
        contact["phone"] = phone
        contact["email"] = email

        save_contacts()
        flash("Contact updated successfully!", "success")

        return redirect(url_for("home"))

    return render_template(
        "index.html",
        contacts=contacts,
        total_contacts=len(contacts),
        search="",
        editing=contact
    )


# Delete a contact
@app.route("/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    contact = find_contact(contact_id)

    if contact is None:
        flash("Contact not found.", "error")
        return redirect(url_for("home"))

    contacts.remove(contact)
    save_contacts()

    flash("Contact deleted successfully!", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)