#!/usr/bin/env bash
# detect.sh <repo_path>
# Outputs JSON: runtime, version_hint, entry, install_cmd, run_cmd, port, framework

REPO="$1"
[ -z "$REPO" ] && echo '{"runtime":"unknown","error":"no path"}' && exit 1
cd "$REPO" || exit 1

runtime="unknown"; version_hint=""; entry=""; install_cmd=""
run_cmd=""; port=3000; framework="unknown"; env_vars="[]"

if [ -f "package.json" ]; then
  runtime="node"
  version_hint=$(node -e "try{console.log(require('./package.json').engines&&require('./package.json').engines.node||'')}catch(e){}" 2>/dev/null)
  dev_script=$(node -e "try{const s=require('./package.json').scripts||{};console.log(s.dev||s.start||'')}catch(e){}" 2>/dev/null)
  deps=$(node -e "try{const d=require('./package.json');const all={...d.dependencies,...d.devDependencies};console.log(Object.keys(all).join(','))}catch(e){}" 2>/dev/null)
  install_cmd="npm install"
  run_cmd="npm run ${dev_script:-start}"
  port=3000
  framework="node"
  echo "$deps" | grep -q "next" && framework="nextjs" && port=3000
  echo "$deps" | grep -q "vite" && framework="vite" && port=5173
  echo "$deps" | grep -q "express" && framework="express" && port=3000
  echo "$deps" | grep -q "react-scripts" && framework="create-react-app" && port=3000

elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
  runtime="python"
  version_hint=$(python3 --version 2>/dev/null | awk '{print $2}')
  install_cmd="pip install -r requirements.txt"
  if [ -f "manage.py" ]; then
    framework="django"; entry="manage.py"
    run_cmd="python manage.py runserver"; port=8000
  elif [ -f "app.py" ] && grep -q "flask\|Flask" app.py 2>/dev/null; then
    framework="flask"; entry="app.py"
    run_cmd="python app.py"; port=5000
  elif [ -f "main.py" ] && grep -q "fastapi\|FastAPI" main.py 2>/dev/null; then
    framework="fastapi"; entry="main.py"
    run_cmd="uvicorn main:app --reload"; port=8000
  elif [ -f "main.py" ]; then
    entry="main.py"; run_cmd="python main.py"; port=8000
  fi

elif [ -f "go.mod" ]; then
  runtime="go"
  version_hint=$(grep "^go " go.mod | awk '{print $2}')
  entry=$(grep -rl "func main()" --include="*.go" | head -1)
  install_cmd="go mod download"
  run_cmd="go run ."
  port=8080
  grep -q "gin-gonic" go.mod && framework="gin"
  grep -q "labstack/echo" go.mod && framework="echo"
  grep -q "gofiber" go.mod && framework="fiber"

elif [ -f "Cargo.toml" ]; then
  runtime="rust"
  entry="src/main.rs"
  install_cmd=""
  run_cmd="cargo run"
  port=8080

elif [ -f "Gemfile" ]; then
  runtime="ruby"
  install_cmd="bundle install"
  run_cmd="ruby app.rb"
  port=4567
  grep -q "rails" Gemfile && framework="rails" && run_cmd="rails server" && port=3000

elif [ -f "pom.xml" ]; then
  runtime="java"
  install_cmd="mvn install"
  run_cmd="mvn spring-boot:run"
  port=8080; framework="spring-boot"

elif [ -f "build.gradle" ]; then
  runtime="java"
  install_cmd="./gradlew build"
  run_cmd="./gradlew bootRun"
  port=8080

elif [ -f "Dockerfile" ]; then
  runtime="docker"
  entry="Dockerfile"
  port=$(grep "EXPOSE" Dockerfile | awk '{print $2}' | head -1)
  [ -z "$port" ] && port=8080
  run_cmd="docker build -t app . && docker run -p ${port}:${port} app"
fi

cat <<EOF
{"runtime":"$runtime","version_hint":"$version_hint","entry":"$entry","install_cmd":"$install_cmd","run_cmd":"$run_cmd","port":$port,"framework":"$framework","env_vars_needed":$env_vars}
EOF