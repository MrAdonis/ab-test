一个项目里如果还在同时维护 webpack.config.js、babel.config.js、jest.config.js、tsconfig 这堆东西，现在大部分可以删掉了——Bun 把运行时、包管理器、打包器、测试框架收进了一个二进制。

我把手头一个项目的依赖从 npm install 换成 bun install，同一份 package.json，装包时间从 40 多秒降到 3 秒左右，这个量级跟 Bun 官方给出的十几倍差距对得上。TypeScript 文件直接 bun run index.ts 就能跑，不用先过一遍 tsc 编译。

上手不用重写项目：bun install 代替 npm install，bun run 代替 npm run，bun test 内置测试直接跑，不用另装 jest。命令跟 npm 基本一一对应，迁移成本低到现在就能试。

工具链配置文件多到想砍的时候，把这条翻出来照着命令走一遍就行。
