/* Incisors Med - interactions + WhatsApp submission routing.
   Pages are static, so every patient form is delivered by handing the composed
   message to WhatsApp for +92 341 0704151. */
(function () {
  "use strict";

  /* assembled from parts so no build step can mask or mangle it */
  var WA_NUMBER = "923410" + "704151";

  var SEDATION_LABEL = {
    standard: "Standard Gentle",
    nitrous: "Nitrous Oxide",
    sleep: "Twilight Sleep IV"
  };

  function waURL(text) {
    return "https://wa.me/" + WA_NUMBER + "?text=" + encodeURIComponent(text);
  }

  function waSend(text) {
    var url = waURL(text);
    var win = null;
    try {
      win = window.open(url, "_blank", "noopener");
    } catch (e) {
      win = null;
    }
    if (!win) {
      window.location.href = url;
    }
    return url;
  }

  function field(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    if (!el) {
      return "";
    }
    return (el.value || "").replace(/\s+/g, " ").trim();
  }

  function reveal(el) {
    if (el) {
      el.classList.remove("hidden");
    }
  }

  /* ---------------------------------------------------------- booking form */
  window.handleBookingSubmit = function (event) {
    event.preventDefault();
    var form = event.target;
    var sedation = form.querySelector('input[name="sedation"]:checked');
    var comfort = sedation
      ? (SEDATION_LABEL[sedation.value] || sedation.value)
      : "Not specified";

    var msg = [
      "\uD83E\uDDB7 *New Appointment Request \u2014 Incisors Med*",
      "",
      "Full Name: " + (field(form, "full_name") || "-"),
      "Phone Number: " + (field(form, "phone") || "-"),
      "Clinic Pavilion: " + (field(form, "clinic") || "-"),
      "Reason for Visit: " + (field(form, "reason") || "-"),
      "Comfort & Sedation: " + comfort,
      "Preferred Date/Time: Not specified",
      "",
      "Submitted from: " + document.title
    ].join("\n");

    waSend(msg);
    reveal(document.getElementById("booking-success"));
    form.reset();
  };

  /* --------------------------------------------------------- portal request */
  window.handlePortalSubmit = function (event) {
    event.preventDefault();
    var form = event.target;
    var msg = [
      "\uD83D\uDD10 *Patient Portal Access Request \u2014 Incisors Med*",
      "",
      "Full Name: " + (field(form, "full_name") || "-"),
      "Phone Number: " + (field(form, "phone") || "-"),
      "Date of Birth: " + (field(form, "dob") || "-"),
      "Home Clinic: " + (field(form, "clinic") || "-"),
      "Reason for Access: " + (field(form, "reason") || "-"),
      "Notes: " + (field(form, "notes") || "-"),
      "",
      "Submitted from: " + document.title
    ].join("\n");

    waSend(msg);
    reveal(document.getElementById("portal-success"));
    form.reset();
  };

  /* ------------------------------------------------------- clinic selector */
  window.selectClinic = function (cardElement, name, slot) {
    document.querySelectorAll(".clinic-card").forEach(function (c) {
      c.classList.remove("border-cyan-500", "shadow-md", "bg-cyan-50/30");
      c.classList.add("border-transparent");
    });
    cardElement.classList.remove("border-transparent");
    cardElement.classList.add("border-cyan-500", "shadow-md", "bg-cyan-50/30");

    var clinicNameEl = document.getElementById("selected-clinic-name");
    var clinicSlotEl = document.getElementById("selected-clinic-slot");
    var formSelectEl = document.getElementById("form-clinic-select");

    if (clinicNameEl) {
      clinicNameEl.textContent = "Selected: " + name;
    }
    if (clinicSlotEl) {
      clinicSlotEl.textContent = "Next available slot: " + slot + " with Specialist Team";
    }
    if (formSelectEl) {
      if (name.indexOf("Downtown") > -1) {
        formSelectEl.value = "Downtown";
      } else if (name.indexOf("West End") > -1) {
        formSelectEl.value = "West End";
      } else if (name.indexOf("North Lake") > -1) {
        formSelectEl.value = "North Lake";
      }
    }
  };

  /* ------------------------------------------------------- insurance check */
  window.verifyCoverage = function () {
    var select = document.getElementById("insurance-carrier");
    var status = document.getElementById("insurance-status");
    if (!select || !select.value) {
      window.alert("Please select a healthcare or dental insurance provider.");
      return;
    }
    if (status) {
      status.classList.remove("hidden");
    }
  };

  /* ------------------------------------------------------------ mobile menu */
  function wireMobileMenu() {
    var toggle = document.getElementById("mobile-menu-toggle");
    var menu = document.getElementById("mobile-menu");
    var icon = document.getElementById("mobile-menu-icon");
    if (!toggle || !menu) {
      return;
    }
    toggle.addEventListener("click", function () {
      var open = menu.classList.toggle("hidden") === false;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (icon) {
        icon.textContent = open ? "close" : "menu";
      }
    });
  }

  /* --------------------------------------------------------- digest sign-up */
  function wireDigest() {
    var btn = document.getElementById("digest-submit");
    var input = document.getElementById("digest-email");
    if (!btn || !input) {
      return;
    }
    btn.addEventListener("click", function () {
      var email = (input.value || "").trim();
      if (!email || email.indexOf("@") < 1) {
        input.focus();
        window.alert("Please enter a valid e-mail address so we can send the digest.");
        return;
      }
      waSend([
        "\uD83D\uDCE9 *Digest Subscription Request \u2014 Incisors Med*",
        "",
        "Email: " + email,
        "",
        "Submitted from: " + document.title
      ].join("\n"));
      input.value = "";
    });
  }

  /* ------------------------------------------------------ external new tabs */
  function hardenExternalLinks() {
    document.querySelectorAll('a[href^="http"]').forEach(function (a) {
      if (a.hostname && a.hostname !== window.location.hostname && !a.hasAttribute("target")) {
        a.setAttribute("rel", "noopener noreferrer");
      }
    });
  }

  function init() {
    wireMobileMenu();
    wireDigest();
    hardenExternalLinks();
    /* keep the visible clinic selection in sync with whichever section is open */
    var first = document.querySelector(".clinic-card.border-cyan-500");
    if (first && !first.dataset.wired) {
      first.dataset.wired = "1";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
