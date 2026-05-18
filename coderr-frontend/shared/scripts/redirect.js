function redirectToOffer(id) {
  if (currentUser) {
    window.location.href = "/offer/?id=" + id;
  } else {
    showToastHint(["Loggen Sie sich bitte ein, um Details zu sehen."]);
  }
}

function redirectToOfferList(search) {
  window.location.href = "/offers/?search=" + search;
}

function redirectToOwnProfile() {
  window.location.href = "/profile/";
}

function redirectToBusinessProfile(id) {
  window.location.href = "/business-profile/?id=" + id;
}

function redirectToCustomerProfile(id) {
  window.location.href = "/customer-profile/?id=" + id;
}
