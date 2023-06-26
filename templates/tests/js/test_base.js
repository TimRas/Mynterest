test('Clicking "Back to Top" button scrolls to the top', () => {
    document.body.innerHTML = `
      <a href="#" class="back-to-top-button"></a>
    `;

    const backToTopButton = document.querySelector('.back-to-top-button');

    // Wait for the document to be fully loaded
    document.addEventListener('DOMContentLoaded', () => {
        backToTopButton.click();

        expect(window.scrollTo).toHaveBeenCalledWith({
            top: 0,
            behavior: 'smooth',
        });
    });
});

test('Alert is closed after a delay', () => {
    document.body.innerHTML = `
      <div id="msg"></div>
    `;

    // Wait for the document to be fully loaded
    document.addEventListener('DOMContentLoaded', () => {
        // Set up fake timers
        jest.useFakeTimers();

        // Run the code that sets the timeout
        setTimeout(() => {
            let messages = document.getElementById('msg');
            let alert = new bootstrap.Alert(messages);
            alert.close();

            expect(global.bootstrap.Alert).toHaveBeenCalledWith(messages);
            expect(alert.close).toHaveBeenCalled();
        }, 1500);

        // Advance timers
        jest.runAllTimers();
    });
});