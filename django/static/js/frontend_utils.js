const firstWordList = ["adorable", "adventurous", "aggressive", "agreeable", "alert", "alive", "amused", "angry", "annoyed", "anxious", "attractive", "average", "bad", "beautiful", "better", "bewildered", "blue", "blushing", "bored", "brainy", "brave", "breakable", "bright", "busy", "calm", "careful", "cautious", "charming", "cheerful", "clean", "clear", "clever", "cloudy", "clumsy", "colourful", "combative", "comfortable", "concerned", "confused", "cooperative", "crazy", "curious", "cute", "dangerous", "delightful", "determined", "different", "distinct", "dizzy", "eager", "easy", "elated", "elegant", "energetic", "enthusiastic", "excited", "expensive", "exuberant", "fair", "faithful", "famous", "fancy", "fantastic", "fine", "friendly", "funny", "gentle", "gifted", "glamorous", "gleaming", "glorious", "good", "gorgeous", "handsome", "happy", "healthy", "helpful", "hilarious", "hungry", "important", "innocent", "jolly", "kind", "light", "lively", "lovely", "lucky", "magnificent", "misty", "muddy", "mushy", "mysterious", "naughty", "nice", "oldfashioned", "outstanding", "perfect", "powerful", "precious", "real", "relieved", "rich", "shiny", "smiling", "sparkling", "successful", "super", "thoughtful", "wandering", "xenogeneic", "young"];
const secondWordList = ["actor", "advertisement", "airport", "animal", "answer", "apple", "ballon", "banana", "battery", "boy", "breakfast", "camera", "candle", "car", "cartoon", "gold", "grass", "guitar", "hamburger", "helicopter", "horse"];

let generateUsernameBtn = document.getElementById('generate-username');
let copyBtn = document.getElementById('copy-btn');

let togglePassword = document.getElementById('togglePassword');
let newPassword1 = document.getElementById('id_new_password1');
let newPassword2 = document.getElementById('id_new_password2');

// profile.html
let editBtn = document.getElementById('edit');
let profileCard = document.getElementById('profile-card');
let editUser = document.getElementById('edit-user');
let cancelBtn = document.getElementById('cancel');

// login.html
let showPassword = document.getElementById('check-password');


function generateRandomUsername() {

    generateUsernameBtn.addEventListener('click', () => {
        let firstUserWord = firstWordList[Math.floor(Math.random() * firstWordList.length)].split(' ').join('');
        let secondUserWord = secondWordList[Math.floor(Math.random() * secondWordList.length)].split(' ').join('');
        document.getElementById('id_username').value = firstUserWord + secondUserWord;
    });
}

function copyToClipboard() {

    const passwordResetLink = copyBtn.getAttribute('data-passwordResetLink');
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(passwordResetLink);
    });
}

function viewPassword() {
    togglePassword.addEventListener('click', () => {
        const type = newPassword1.getAttribute('type') === 'password' ? 'text' : 'password';
        const classAttribute = togglePassword.getAttribute('class') === 'bi-eye' ? 'bi-eye-slash' : 'bi-eye';
        newPassword1.setAttribute('type', type);
        newPassword2.setAttribute('type', type);
        togglePassword.setAttribute('class', classAttribute);
    })
}

// profile.html
function slideToLeft() {
    editBtn.addEventListener('click', () => {
        profileCard.style.transform = 'translateX(0%)';
        setTimeout(fadeIn, 1000);
    });
}

function slideToRight() {
    cancelBtn.addEventListener('click', () => {
       editUser.style.visibility = 'hidden';
       profileCard.style.transform = 'translateX(55%)'
       setTimeout(showEditBtn, 1000);
    });
}

function fadeIn() {
    editUser.style.visibility = 'visible';
    editBtn.style.display = 'none';
}

function showEditBtn() {
    editBtn.style.display = 'inline';
}

// login.html
function showLoginPassword() {
    let loginPasswordInput = document.getElementById('typePasswordX');
    showPassword.addEventListener('click', () => {
        const passwordType = loginPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        loginPasswordInput.setAttribute('type', passwordType);
    });
}

document.addEventListener('DOMContentLoaded', generateRandomUsername);
document.addEventListener('DOMContentLoaded', copyToClipboard);
document.addEventListener('DOMContentLoaded', viewPassword);
document.addEventListener('DOMContentLoaded', slideToLeft);
document.addEventListener('DOMContentLoaded', slideToRight);
document.addEventListener('DOMContentLoaded', showLoginPassword);