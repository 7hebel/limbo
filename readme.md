<div align="center">
    <br>
    <img src="./assets/logo.png" width="280" alt="Limbo" />
    <br>
    <br>
    <h2>Limbo.</h2>
    <h4>JiT interpreted and compiled, node-based programming environment.</h4>
</div>

![App](https://raw.githubusercontent.com/7hebel/limbo/refs/heads/main/assets/ss-app.png)

<div align="center">
    <br>
    <h2>✨ About</h2>
</div>

**Limbo** is a programming environment that allows You to create simple programs using user friendly text interface in the terminal. There is **no code**, just node blocks with the input and output sources that You can connect together.

<div align="center">
    <br>
    <h2>📦 Install</h2>
</div>

1. Ensure [Python](https://www.python.org/downloads/) is installed and added to the PATH.

2. Clone the repository:
   
   ```bash
   git clone https://github.com/7hebel/limbo.git
   ```
   
   or download as a ZIP and unpack.

3. Install the required dependencies:
   
   Open the terminal and navigate to the limbo's directory.
   
   ```bash
   pip install -r requirements.txt
   ```

4. Run limbo:
   
   ```bash
   py main.py  (replace py with python3 on linux)
   ```

<div align="center">
    <br>
    <h2>🔎 Test program</h2>
</div>

Import one of the templates located in the `templates/` directory to check how program works.

```bash
py main.py templates/calc.limb
```

<div align="center">
    <br>
    <h2>👁️ User Interface</h2>
</div>

### 1. Sidebar

Sidebar is located on the left side of the app and contains all the available nodes that You can use in the program. 

##### 🧭 Navigation.

To move focus to the sidebar, press `tab`.

Navigate through the nodes using `↕` and `ctrl + ↕` to skip a entire collection. Fold collections with `↔` and spawn new nodes with `enter` or `space`.

You can fold the entire sidebar using `ctrl + b`

##### ✨ Icons.

Next to the node's title is located a **output-based icon**:

- `ƒ` - **Function node** - returns a value (color represents data type)

- `λ` - **Flow node** - doesn't return any value but provides a Flow output.

- ` ` - **Exit node** - if there is no icon, node does not provide any output at all and will end program's flow.

### 2. Viewport

It occupies almost entire screen's space and is used to display and alter nodes.

##### 🧭 Navigation.

You can shift the camera using `ctrl + ←↑→↓` or move selected node with `alt + ←↑→↓`. To select a node, shift focus from other nodes using `←↑→↓`. The algorithm will choose the closest node in given direction. **Selected node**'s outline is colored and all wires connecting this node will be undimmed.

##### 📝 Editing nodes.

Spawn new nodes from sidebar. To enter a `EDIT NODE` mode press `enter`. Use `←↑→↓` to shift focus between the sources. To connect sources, press `space` on selected source and navigate to it's designated destination source in other node. Select the second node's source and press `space` again to connect the endpoints. 

*Remember that both sources must have same data type (color)*. 

To set a **constant value** press `c` on the selected `input` source and type a value. Exit `EDIT MODE` with `esc`.

##### 🗃️ Workspace.

You can export workspace using `ctrl + e` and import another with `ctrl + i`. If there is no file associated with this workspace, You will be asked to provide name (path). Close the current workspace with `ctrl + w`.

##### 👟 Run the program.

Press `F1` to run the current program starting from a `START` node. You can also compile a program to the `.exe` using `F2` (it should take ~30s). There is also a built-in debugger (start with `F12`) that will run the interpreted version of the program but will also display a current state of the interpreter and the execution process of each individual node.

### 3. Status bar

Below the main viewport, You can see the status bar displaying either a feedback from Your previous actions (like saving a file or altering a node) or keyboard shortcuts available in the current context.

<div align="center">
    <br>
    <h2>🔢 Data types</h2>
</div>

Data type describes a type of data stored inside the source. They can be distinguished by a color and the name. There are 4 data types in Limbo.

- `TEXT` (yellow) - Represents standard text provided by user or set as a constant value.

- `NUMBER` (purple) - Represents numbers and is used for  a mathematical operations. (*all numbers are treated as a floating-point*)

- `BOOLEAN` (blue) - Logical value, either True or False.

- `FLOW` (red) - Special type not representing data but a runtime flow direction. It is used to point the next node that should be executed without passing any input data to it.

##### 🔁 Cast types.

Use nodes from the `Cast` collection to switch data types. 

It is not always possible to cast a text to a number, as text may contain invalid characters. Transformer will try to use all numbers and skip all the text characters but it still may fail. That's why You can provide the `default` value that will be used instead. When conversion fails and the `default` value is not provided, program will terminate with a `ERROR` status.

<div align="center">
    <br>
    <h2>🧠 Memory</h2>
</div>

There is a entire collection of the nodes called `Memory`. It provides variable-like storage functionality to the program. At the start of the program, new **memory jar** is created. A memory jar is a key-value database. The `RESTART` node has a `Save memory` boolean input that if set to True, will not flush current memory state but start program with current memory jar.

<div align="center">
    <br>
    <h2>⛔ Exit codes</h2>
</div>

All codes greater or equal 0 are considered as a `success` and negative codes means `fail`. The exit code defines a reason of exit.

Default codes:

- `0` - OK

- `-1` - Runtime error.

- `-2` - Infinite recursion terminated.

- `-3` - Manual termination.

- `10` - Restart program

- `11` - Restart program and save memory

The `RESTART` node does the same thing as a `EXIT` with a code set to either `10` or `11`.

<div align="center">
    <br>
    <h2>🪲 Debugger</h2>
</div>

![App](https://raw.githubusercontent.com/7hebel/limbo/refs/heads/main/assets/ss-debugger.png)

<div align="center">
    <br>
    <h2>📄 .limb format</h2>
</div>

You can export the current workspace state into a file written in the custom `.limb` format. Format uses byte symbols, so it might not be displayed correctly in all text editors (use hex editors).

📝 Format syntax.

`LIMB\0` - File header.

`\CAM6,34` - Camera position (x=6, y=34)

`\NT,abc,xyz,9,23\0\Oabc/srcOut\>def/srcIn\0\0\Cabc/srcIn\>value\0` - Each node

`\EOF` - End of file.

Node format:

| Token       | Description                                        |
| ----------- | -------------------------------------------------- |
| `\N`        | Node header                                        |
| `T`         | Is standard node? (`T` for True or `F` for False)  |
| `,`         | Value separator                                    |
| `abc`       | Node's instance ID                                 |
| `,`         | Value separator                                    |
| `xyz`       | Node's factory ID                                  |
| `,`         | Value separator                                    |
| `9,23`      | Node's position in the format `x=9, y=23`          |
| `,`         | Value separator                                    |
| `\0`        | End of metadata section                            |
| `\O`        | Output header                                      |
| `abc`       | Output node's ID (matches node instance ID above)  |
| `/`         | Separator                                          |
| `srcOut`    | Name of output source (example: `srcOut`)          |
| `\>`        | Source pointer                                     |
| `def`       | Wire's target node's ID (example: `def`)           |
| `/`         | Separator                                          |
| `srcIn`     | Name of source wire connects to (example: `srcIn`) |
| `\0`        | End of wire data                                   |
| `\0`        | End of outputs section                             |
| `\C`        | Constant values header                             |
| `abc/srcIn` | Node ID/source name in `nodeID/sourceName` format  |
| `\>`        | Pointer                                            |
| `value`     | Constant value (const example: `value`)            |
| `\0`        | End of constant value                              |

(might contain multiple constants separated by `\0` or no constants where file node ends on `\C`)
