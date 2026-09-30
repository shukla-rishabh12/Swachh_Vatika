{% extends "base.html" %}
{% block title %}My Profile — Swachh-Seva{% endblock %}
{% block body_role %}WORKER{% endblock %}
{% block page_title %}Profile{% endblock %}

{% block content %}
<div class="page-wrapper">
  <form id="profile-form" class="card form-card" novalidate>

    <h2>👤 Worker Profile</h2>
    <p class="muted" style="margin-bottom:20px;">Keep your contact details updated.</p>

    <div class="form-group">
      <label>Email (read-only)</label>
      <input id="email" type="text" readonly />
    </div>

    <div class="form-group">
      <label for="full_name">Full Name *</label>
      <input id="full_name" type="text" required />
    </div>

    <div class="form-group">
      <label for="phone">Phone</label>
      <input id="phone" type="tel" placeholder="10-digit number" />
    </div>

    <div class="form-group">
      <label for="address">Address</label>
      <textarea id="address" rows="2"></textarea>
    </div>

    <div class="form-group">
      <label for="city">City</label>
      <input id="city" type="text" />
    </div>

    <div id="form-error" class="form-error" style="display:none;"></div>
    <div id="form-success" class="form-success" style="display:none;"></div>

    <div class="form-actions">
      <button type="submit" id="save-btn" class="btn-primary">Save Changes</button>
    </div>
  </form>
</div>
{% endblock %}

{% block scripts %}
<script src="/static/js/worker/profile.js"></script>
{% endblock %}