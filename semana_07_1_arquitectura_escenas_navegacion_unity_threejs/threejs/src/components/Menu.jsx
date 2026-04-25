import { Link } from "react-router-dom";

function Menu() {
  return (
    <div className="pantalla">
      <h1>MENÚ PRINCIPAL</h1>

      <div className="botones">
        <Link to="/juego">
          <button>Jugar</button>
        </Link>

        <Link to="/creditos">
          <button>Créditos</button>
        </Link>
      </div>
    </div>
  );
}

export default Menu;