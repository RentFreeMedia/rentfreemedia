document.getElementById('submit').disabled = true;

var DOMAIN = window.location.origin;

var changeLoadingState = function(isLoading) {
if (isLoading) {
	document.getElementById('submit').disabled = true;
    document.getElementById('spinner').classList.remove('d-none');
    document.getElementById('button-text').classList.add('d-none');
  } else {
    document.getElementById('submit').disabled = false;
    document.getElementById('spinner').classList.add('d-none');
    document.getElementById('button-text').classList.remove('d-none');
  }
};

var planSelect = function(elid, name, price, prodtier) {

    var pln = document.getElementById('plan');
    var prce = document.getElementById('price');
    var prod_tier = document.getElementById('prodtier');
    var element = document.getElementById(elid);
    var actives = document.getElementsByClassName('active');

    pln.innerHTML = name;
    prce.innerHTML = price;
    prod_tier.value = prodtier;
        document.getElementById('submit').disabled = false;
        while(actives.length > 0){
    		actives[0].classList.remove('active');
		}
        element.classList.add('active');
};

fetch('/subscribe-stripe-config/')
	.then(function(result) { return result.json(); })
	.then(function(data) {
	  	// Initialize Stripe.js
	const stripe = Stripe(data.publicKey);

	var paymentForm = document.getElementById('subscribe-new-form');
	if (paymentForm) {

		paymentForm.addEventListener('submit', function (event) {
			event.preventDefault();
			changeLoadingState(true);

			fetch('/subscribe-checkout-session/', {
				method: 'POST',
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value,
				},
				credentials: 'same-origin',
				body: JSON.stringify({
					"product_tier": document.getElementById('prodtier').value,
					"domain": DOMAIN,
				})
			}).then(function(result) { return result.json(); }).then(function(data) {
            	stripe.redirectToCheckout(
                	{
                    	sessionId: data.sessionId
                	}
              	);
          	});
        });
	}
});
