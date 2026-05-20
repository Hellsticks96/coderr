function getLogedInHeaderTemplate() {
  return `<img onclick="toggleOpen(this); stopProp(event)" closable="true" open="false" class="profile_img_small" src="${getPersonImgPath(currentUser.file)}" alt="Profilbild">
            <div class="menu_content d_flex_cc_gm f_d_c">
                <a href="/profile/">Mein Profil</a>
                <p onclick="logOut()">Ausloggen</p>
            </div>`;
}

function getLogedOutHeaderTemplate() {
  const currentPath = window.location.pathname;

  if (currentPath === "/login/") {
    return `
        <div class="d_flex_cc_gm">
            <a href="/register/" class="std_btn btn_prime pad_s  font_white_color">Registrieren</a>
        </div>`;
  } else if (currentPath === "/register/") {
    return `
        <div class="d_flex_cc_gm">
            <a href="/login/" class="std_btn btn_secondary pad_s ">Login</a>
        </div>`;
  } else {
    return `
            <div class="d_flex_cc_gm">
                <a href="/login/" class="std_btn btn_secondary pad_s ">Login</a>
                <a href="/register/" class="std_btn btn_prime pad_s  font_white_color">Registrieren</a>
            </div>`;
  }
}
