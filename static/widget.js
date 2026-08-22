// static/widget.js
(function () {
  "use strict";

  // Extract widget ID from the script tag's src
  var scripts = document.getElementsByTagName("script");
  var currentScript = scripts[scripts.length - 1];
  var src = currentScript.getAttribute("src");
  var urlParams = new URL(src, window.location.href).searchParams;
  var widgetId = urlParams.get("id");

  if (!widgetId) {
    console.error("[Widget] No widget ID provided in script src");
    return;
  }

  // Determine API base URL from script src
  var scriptUrl = new URL(src, window.location.href);
  var API_BASE = scriptUrl.origin;

  // Fetch widget config
  fetch(API_BASE + "/api/widgets/" + widgetId + "/config", {
    method: "GET",
    headers: { Accept: "application/json" },
  })
    .then(function (res) {
      if (!res.ok) throw new Error("Failed to load widget config: " + res.status);
      return res.json();
    })
    .then(function (config) {
      renderWidget(config);
    })
    .catch(function (err) {
      console.error("[Widget] Error loading config:", err);
    });

  function renderWidget(config) {
    // Create container
    var container = document.createElement("div");
    container.id = "flyrank-widget-" + widgetId;
    container.style.cssText =
      "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; " +
      "max-width: 450px; margin: 20px auto; padding: 24px; " +
      "border: 1px solid #e0e0e0; border-radius: 8px; " +
      "background: #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.1);";

    // Title
    var title = document.createElement("h3");
    title.textContent = config.title;
    title.style.cssText = "margin: 0 0 8px 0; color: #333; font-size: 20px;";
    container.appendChild(title);

    // Description
    if (config.description) {
      var desc = document.createElement("p");
      desc.textContent = config.description;
      desc.style.cssText = "margin: 0 0 16px 0; color: #666; font-size: 14px;";
      container.appendChild(desc);
    }

    // Form
    var form = document.createElement("form");
    form.id = "flyrank-form-" + widgetId;

    // Render fields from config
    var fields = config.fields_config || [];
    fields.forEach(function (field) {
      var wrapper = document.createElement("div");
      wrapper.style.cssText = "margin-bottom: 12px;";

      var label = document.createElement("label");
      label.textContent = field.label + (field.required ? " *" : "");
      label.style.cssText =
        "display: block; margin-bottom: 4px; font-size: 14px; color: #444; font-weight: 500;";
      wrapper.appendChild(label);

      var input;
      if (field.field_type === "textarea") {
        input = document.createElement("textarea");
        input.rows = 3;
      } else if (field.field_type === "select" && field.options) {
        input = document.createElement("select");
        var defaultOpt = document.createElement("option");
        defaultOpt.value = "";
        defaultOpt.textContent = field.placeholder || "Select...";
        input.appendChild(defaultOpt);
        field.options.forEach(function (opt) {
          var o = document.createElement("option");
          o.value = opt;
          o.textContent = opt;
          input.appendChild(o);
        });
      } else {
        input = document.createElement("input");
        input.type = field.field_type || "text";
        if (field.placeholder) input.placeholder = field.placeholder;
      }

      input.name = field.name;
      input.required = field.required;
      input.style.cssText =
        "width: 100%; padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px; " +
        "font-size: 14px; box-sizing: border-box;";
      wrapper.appendChild(input);
      form.appendChild(wrapper);
    });

    // Honeypot field (hidden — bots fill it, humans don't)
    var honeypot = document.createElement("input");
    honeypot.type = "text";
    honeypot.name = "_hp_field";
    honeypot.tabIndex = -1;
    honeypot.autocomplete = "off";
    honeypot.style.cssText =
      "position: absolute; left: -9999px; width: 1px; height: 1px; opacity: 0;";
    form.appendChild(honeypot);

    // Submit button
    var btn = document.createElement("button");
    btn.type = "submit";
    btn.textContent = config.button_text || "Submit";
    btn.style.cssText =
      "width: 100%; padding: 10px; background: #4F46E5; color: white; border: none; " +
      "border-radius: 4px; font-size: 16px; cursor: pointer; font-weight: 600;";
    form.appendChild(btn);

    // Status message
    var statusDiv = document.createElement("div");
    statusDiv.id = "flyrank-status-" + widgetId;
    statusDiv.style.cssText = "margin-top: 12px; font-size: 14px; text-align: center;";
    form.appendChild(statusDiv);

    // Handle form submission
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      btn.disabled = true;
      btn.textContent = "Submitting...";
      statusDiv.textContent = "";
      statusDiv.style.color = "#666";

      // Collect form data
      var formData = {};
      fields.forEach(function (field) {
        var el = form.elements[field.name];
        if (el) formData[field.name] = el.value;
      });

      var payload = {
        widget_id: widgetId,
        data: formData,
        _hp_field: honeypot.value,
      };

      fetch(API_BASE + "/api/submissions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
        .then(function (res) {
          if (res.status === 429) {
            statusDiv.textContent = "Too many submissions. Please wait a moment.";
            statusDiv.style.color = "#dc2626";
            return null;
          }
          if (!res.ok) {
            return res.json().then(function (err) {
              throw new Error(err.detail || "Submission failed");
            });
          }
          return res.json();
        })
        .then(function (result) {
          if (result) {
            statusDiv.textContent = "Thank you! Your submission was received.";
            statusDiv.style.color = "#16a34a";
            form.reset();
          }
        })
        .catch(function (err) {
          statusDiv.textContent = err.message || "Something went wrong. Please try again.";
          statusDiv.style.color = "#dc2626";
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = config.button_text || "Submit";
        });
    });

    container.appendChild(form);

    // Insert widget into the page
    currentScript.parentNode.insertBefore(container, currentScript.nextSibling);
  }
})();