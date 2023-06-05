## Frontend React JS

### Switch to the frontend directory
```bash
cd frontend-react-js
```

### Install the project dependencies
```bash
npm install
```

### Reviewing the Project Structure

Once our project files have been created and our dependencies have been installed, our project structure should look like this:

```bash
frontend-react-js
├ node_modules
├ public
├ src
├ .env.example
├ .gitignore
├ Dockerfile
├ package-lock.json
├ package.json
└ README.md
```

#### What are each of these files and folders for?

`README.md` is a markdown file that includes a lot of helpful tips and links that can help you while learning to use Create React App.

`node_modules` is a folder that includes all of the dependency-related code that Create React App has installed.

`package.json` that manages our app dependencies and what is included in our node_modules folder for our project, plus the scripts we need to run our app.

`.gitignore` is a file that is used to exclude files and folders from being tracked by Git.

`public` is a folder that we can use to store our static assets, such as images, svgs, and fonts for our React app.

`src` is a folder that contains our source code. It is where all of our React-related code will live and is what we will primarily work in to build our app.

### To start your React project, you can simply run:

`npm start`

When we run our project, a new browser tab will automatically open on our computer's default browser to view our app.

The development server will start up on `localhost:3000` and, right away, we can see the starting home page for our app.
