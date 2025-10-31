// Dynamic typing animation
document.addEventListener("DOMContentLoaded", () => {
    const roles = [
        "Full Stack Developer 💻",
        "Python & Flask Expert 🐍",
        "Creative Thinker 🎨",
        "Problem Solver ⚙️"
    ];
    let i = 0, j = 0, current = "", isDeleting = false;
    const el = document.getElementById("typed");

    function typeEffect() {
        const fullText = roles[i];
        if (isDeleting) {
            current = fullText.substring(0, j--);
        } else {
            current = fullText.substring(0, j++);
        }
        el.textContent = current;

        if (!isDeleting && j === fullText.length) {
            isDeleting = true;
            setTimeout(typeEffect, 1200);
        } else if (isDeleting && j === 0) {
            isDeleting = false;
            i = (i + 1) % roles.length;
            setTimeout(typeEffect, 300);
        } else {
            setTimeout(typeEffect, isDeleting ? 50 : 100);
        }
    }

    typeEffect();
});
