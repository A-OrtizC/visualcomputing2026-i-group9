import { Link } from "react-router-dom";

function Creditos() {
  return (
    <div className="pantalla">
      <h1>CRÉDITOS</h1>

      <p>Hecho por: Alejandro Ortiz Cortes</p>
      <p>Agradecimientos a: Documentación Threejs</p>

      <Link to="/">
        <button>Volver al menú</button>
      </Link>
    </div>
  );
}

export default Creditos;