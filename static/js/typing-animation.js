// Initialize the typing animation
document.addEventListener('DOMContentLoaded', function() {
    // Add a small delay to ensure everything is loaded
    setTimeout(() => {
        const typingAnimationElement = document.getElementById('typing-animation');
        
        if (!typingAnimationElement) {
            console.warn('Typing animation element not found');
            return;
        }

    // Create an array of typing text
    const typingTexts = [
        'Engineer',
        'Analyst', 
        'Data Enthusiast',
    ];

    let currentTextIndex = 0;
    let currentCharIndex = 0;
    let isDeleting = false;
    let typingSpeed = 80; // Speed for typing - made faster for smoothness
    let deletingSpeed = 60; // Speed for deleting - made faster for smoothness
    let pauseTime = 1500; // Time to pause between words - reduced for better flow

    function typeText() {
        const currentText = typingTexts[currentTextIndex];
        
        if (isDeleting) {
            // Delete characters
            typingAnimationElement.textContent = currentText.substring(0, currentCharIndex - 1);
            currentCharIndex--;
        } else {
            // Type characters
            typingAnimationElement.textContent = currentText.substring(0, currentCharIndex + 1);
            currentCharIndex++;
        }

        // Add cursor class when typing, remove when deleting
        if (!isDeleting && currentCharIndex > 0) {
            typingAnimationElement.classList.add('cursor');
        } else if (isDeleting && currentCharIndex === 0) {
            typingAnimationElement.classList.remove('cursor');
        }

        let speed = isDeleting ? deletingSpeed : typingSpeed;

        if (!isDeleting && currentCharIndex === currentText.length) {
            // Finished typing, pause then start deleting
            speed = pauseTime;
            isDeleting = true;
        } else if (isDeleting && currentCharIndex === 0) {
            // Finished deleting, move to next word
            isDeleting = false;
            currentTextIndex = (currentTextIndex + 1) % typingTexts.length;
            speed = 300; // Reduced pause before starting next word for smoother flow
        }

        setTimeout(typeText, speed);
    }

    // Start the typing animation
    typeText();
    }, 100); // 100ms delay
});