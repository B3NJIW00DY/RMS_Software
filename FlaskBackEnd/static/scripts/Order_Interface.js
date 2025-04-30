// Example price list
const prices = {
    'Garlic Bread': 4.00,
    'Soup': 3.50,
    'Bruschetta': 5.00,
    'Burger': 8.00,
    'Pizza': 9.00,
    'Steak': 15.00,
    'Ice Cream': 3.00,
    'Cake': 4.00,
    'Brownie': 4.50,
    'Coke': 2.00,
    'Lemonade': 2.00,
    'Water': 1.00
};

let currentOrder = []; // stores {name, quantity}
const savedOrders = {}; // stores orders per table number

function addToOrder(itemName, quantityInputId) {
    const quantity = parseInt(document.getElementById(quantityInputId).value);
    if (isNaN(quantity) || quantity <= 0) {
        alert('Please enter a valid quantity.');
        return;
    }

    // Check if item already exists
    const existingItem = currentOrder.find(item => item.name === itemName);
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        currentOrder.push({ name: itemName, quantity: quantity });
    }

    updateOrderList();
}

function removeFromOrder(itemName) {
    currentOrder = currentOrder.filter(item => item.name !== itemName);
    updateOrderList();
}

function updateOrderList() {
    const orderItemsList = document.getElementById('order-items');
    const hiddenFields = document.getElementById('hidden-fields');
    const totalPriceDisplay = document.getElementById('total-price');

    // Clear current displayed list
    orderItemsList.innerHTML = '';
    hiddenFields.innerHTML = '';

    let total = 0;

    // Rebuild the list
    currentOrder.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `${item.name} x${item.quantity} ($${(prices[item.name] * item.quantity).toFixed(2)}) `;

        // Create remove button
        const removeBtn = document.createElement('button');
        removeBtn.textContent = 'Remove';
        removeBtn.className = 'remove-btn';
        removeBtn.type = 'button';
        removeBtn.onclick = () => removeFromOrder(item.name);

        li.appendChild(removeBtn);
        orderItemsList.appendChild(li);

        // Create hidden input for each item
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'items[]';
        hiddenInput.value = `${item.name}:${item.quantity}`;
        hiddenFields.appendChild(hiddenInput);

        total += prices[item.name] * item.quantity;
    });

    // Update total price
    totalPriceDisplay.textContent = `Total: $${total.toFixed(2)}`;
}

// When page loads
document.addEventListener('DOMContentLoaded', function () {
    const tableSelect = document.getElementById('table-select');

    tableSelect.addEventListener('change', function () {
        const tableNumber = tableSelect.value;

        if (savedOrders[tableNumber]) {
            // Load existing order
            currentOrder = JSON.parse(JSON.stringify(savedOrders[tableNumber])); // deep copy
            alert(`Loaded order for Table ${tableNumber}`);
        } else {
            // No previous order, clear
            currentOrder = [];
        }
        updateOrderList();
    });

    const submitBtn = document.querySelector('.submit-order-btn');
    submitBtn.addEventListener('click', function () {
        const tableNumber = document.getElementById('table-select').value;

        if (currentOrder.length === 0) {
            alert('Cannot submit an empty order!');
            return;
        }

        // Save current order to savedOrders
        savedOrders[tableNumber] = JSON.parse(JSON.stringify(currentOrder)); // deep copy

        // Now also send to server
        submitOrderToServer();
    });

    const clearBtn = document.querySelector('.clear-order-btn');
    clearBtn.addEventListener('click', function () {
        currentOrder = [];
        updateOrderList();
    });
});

// Submit order to server
function submitOrderToServer() {
    const tableNumber = document.getElementById('table-select').value;
    const formData = new FormData();

    formData.append('table', tableNumber);
    currentOrder.forEach(item => {
        formData.append('items[]', `${item.name}:${item.quantity}`);
    });

    fetch('/submit_order', {
        method: 'POST',
        body: formData
    })
        .then(response => response.text())
        .then(data => {
            alert(data); // Show server response
        })
        .catch(error => {
            console.error('Error submitting order:', error);
            alert('Error submitting order. Please try again.');
        });
}

