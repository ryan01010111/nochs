
const categoryHeaders = document.querySelectorAll('.categoryHeader');
const menuItem = document.querySelectorAll('.menu-item');
const addItemContainer = document.querySelector('#addItemContainer');
const closeAddItemBtn = document.querySelector('#closeAddItemBtn');
const scrollIndicator = document.querySelector('#scroll-indicator');
const addItemForm = document.querySelector('#addItemForm');
const addItemId = document.querySelector('#addItemId');
const selectedItemCategory = document.querySelector('#selected-item-category');
const selectedItemStyle = document.querySelector('#selected-item-style');
const toppingsSelect = document.querySelector('#toppings-select');
const subExtrasSelect = document.querySelector('#sub-extras-select');
const toppingInputs = document.querySelectorAll('input[name="topping"]');
const subExtrasInputs = document.querySelectorAll('input[name="extra"]');
const sizeInputs = document.querySelectorAll('input[name="size"]');
const selectedItemPriceSmall = document.querySelector('#selected-item-price-small');
const selectedItemPriceLarge = document.querySelector('#selected-item-price-large');
const addItemQty = document.querySelector('#addItemQty');
const cartItemCounter = document.querySelector('#cartItemCounter');
const showItemAdded = document.querySelector('#showItemAdded');

// event listeners
categoryHeaders.forEach(el => {

    el.addEventListener('click', function() {

        document.querySelectorAll('.categoryContent').forEach(sect => {

            sect.style.display = 'none';
            sect.classList.add('animate-categoryContent');
        });
        document.querySelectorAll('.categoryHeader').forEach(sect => {

            sect.classList.remove('border-flag');
        });
        let content = document.querySelector(`#${this.dataset.showHide}`);
        content.style.display = 'grid';
        setTimeout(() => {content.classList.remove('animate-categoryContent')}, 100 );
        this.classList.add('border-flag');
    });
});


menuItem.forEach(el => {

    el.addEventListener('click', () => {

        addItemForm.reset();
        addItemQty.value = 1;
        showAddItem(el);
        addItemContainer.scrollTop = 0;
        if (addItemContainer.scrollHeight > addItemContainer.offsetHeight + 30) {

            scrollIndicator.classList.remove('hide-element');

        } else {

            scrollIndicator.classList.add('hide-element');
        }
    });
});


closeAddItemBtn.addEventListener('click', () => {

    addItemContainer.classList.add('hide-element');
});


addItemForm.addEventListener('submit', addOrderItem);
addItemForm.addEventListener('submit', (e) => {e.preventDefault()});

addItemContainer.addEventListener('scroll', () => {

    if (addItemContainer.scrollTop >= 50) {

        scrollIndicator.classList.add('hide-element');

    } else if (addItemContainer.scrollHeight > addItemContainer.offsetHeight + 30) {

        scrollIndicator.classList.remove('hide-element');
    }
});


// function declarations
function limitToppings(limit) {

    toppingInputs.forEach(el => {

        el.addEventListener('change', () => {

            var checkedCounter = 0;
            toppingInputs.forEach((tp) => {

                checkedCounter += tp.checked ? 1 : 0;
                if (checkedCounter > limit) {

                    return;
                }
            });

            if (checkedCounter > limit) {

                el.checked = false;
            }
        });
    });
}


function showAddItem(el) {

    toppingsSelect.classList.add('hide-element');
    subExtrasSelect.classList.add('hide-element');
    addItemId.value = el.dataset.itemId;
    selectedItemCategory.innerHTML = el.dataset.menuCategory;
    selectedItemStyle.innerHTML = el.dataset.style;

    if (el.dataset.menuCategory === 'Regular Pizza' || el.dataset.menuCategory === 'Sicilian Pizza') {

        const toppingsQty = +el.dataset.toppingsQty;

        if (toppingsQty !== 0) {

            document.querySelector('#displayToppingsQty').innerHTML = toppingsQty > 1 ? `Select ${toppingsQty} Toppings` : `Select ${toppingsQty} Topping`;
            toppingsSelect.classList.remove('hide-element');
            limitToppings(toppingsQty);
        }

    } else if (el.dataset.menuCategory === 'Sub') {

        subExtrasSelect.classList.remove('hide-element');   
    }

    if (!el.dataset.priceSmall || +el.dataset.priceSmall === 0) {

        selectedItemPriceSmall.parentElement.classList.add('hide-element');

    } else {

        selectedItemPriceSmall.innerHTML = `Small: $${el.dataset.priceSmall}`;
        selectedItemPriceSmall.parentElement.classList.remove('hide-element');
    }

    if (!el.dataset.priceLarge || +el.dataset.priceLarge === 0) {

        selectedItemPriceSmall.innerHTML = '$' + el.dataset.priceSmall;
        selectedItemPriceLarge.parentElement.classList.add('hide-element');

    } else {

        selectedItemPriceLarge.innerHTML = `Large: $${el.dataset.priceLarge}`;
        selectedItemPriceLarge.parentElement.classList.remove('hide-element');
    }

    addItemContainer.classList.remove('hide-element');
}


function addOrderItem(evt) {

    const request = new XMLHttpRequest();
    const itemId = addItemId.value;

    const toppings = [];
    toppingInputs.forEach(el => {

        if (el.checked) {

            toppings.push(el.value);
        }
    });

    const sub_extras = [];
    subExtrasInputs.forEach(el => {

        if (el.checked) {

            sub_extras.push(el.value);
        }
    });

    var size = '';
    sizeInputs.forEach(el => {

        if (el.checked) {
            
            size = el.value;
        }
    });

    const qty = addItemQty.value;

    request.open('POST', '/add_order_item');

    request.onload = () => {

        const data = JSON.parse(request.responseText);

        if (data.success) {

            if (cartItemCounter.classList.contains('hide-element')){
                
                cartItemCounter.classList.remove('hide-element');
            }
            cartItemCounter.innerHTML = data.itemCount;
            cartItemCounter.classList.add('animate-shadow-small');
            setTimeout(() => {cartItemCounter.classList.remove('animate-shadow-small')}, 1500);
            showItemAdded.classList.remove('hide-element');
            showItemAdded.classList.remove('animate-slide-down');
            setTimeout(() => showItemAdded.classList.add('hide-element', 'animate-slide-down'), 2400);

        } else {

            alert('Something went wrong - please try again');
        }

        addItemForm.reset();
        addItemContainer.classList.add('hide-element');
};

    const data = new FormData();
    const itemData = {

        "itemId": itemId,
        "toppings": toppings,
        "sub_extras": sub_extras,
        "size": size,
        "qty": qty
    };

    data.append('itemData', JSON.stringify(itemData));
    
    const csrftoken = Cookies.get('csrftoken');
    request.setRequestHeader('X-CSRFToken', csrftoken);
    request.send(data);
}
