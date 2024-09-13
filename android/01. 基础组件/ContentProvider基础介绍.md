[toc]

## ContentProvider介绍

跟Broadcast一样，它也是应用程序间通信组件，他用于在不同应用间共享数据（也即：IPC跨进程通信），借助ContentProvider，应用可以将内部的数据暴露给外部应用，或者从其它应用中读取共享的数据。



ContentProvider 通过一种标准化的接口提供数据访问能力，确保不同进程之间的数据交互能够安全地进行。



原理：

ContentProvider 的底层工作原理是基于 **Binder** 机制的

当一个进程（客户端）想要通过 ContentProvider 访问另一个进程（服务端）的数据时，Android 系统会通过 Binder 进行跨进程的通信。

客户端进程调用 ContentProvider 的方法时，实际上会通过 Binder 将请求发送到服务端进程。

服务端进程接收请求后，调用相应的 ContentProvider 数据库查询或其他数据操作，并将结果通过 Binder 返回给客户端进程。



## 知识点介绍

![img](https://camo.githubusercontent.com/392fcda044da79bef6f6510966b744f963a421f41bf81cd75b5bbcb07026b3ef/687474703a2f2f75706c6f61642d696d616765732e6a69616e7368752e696f2f75706c6f61645f696d616765732f3934343336352d356339623065326562656433366333662e706e673f696d6167654d6f6772322f6175746f2d6f7269656e742f7374726970253743696d61676556696577322f322f772f31323430)

### URI

#### URI 的定义

**URI (Uniform Resource Identifier)** 是统一资源标识符，用来唯一标识某个资源。在 ContentProvider 中，URI 主要用于标识数据来源，比如标识某个数据库表、记录等。

#### URI 的结构

从图片的示例来看，URI 的结构可以分为以下几个部分：

```
less


复制代码
content://com.carson.provider/User/1
```

#### 解释：

- **content**: 这是 URI 的 **schema**，表示这是一个 ContentProvider。Android 系统规定，所有 ContentProvider 的 URI 都以 `content://` 开头。
- **com.carson.provider**: 这是 **授权信息**，也称为 Authority，表示 ContentProvider 的唯一标识符。每个 ContentProvider 都有一个独一无二的 Authority，通常是包名或包名后缀。
- **User**: 这是 **表名**，表示 ContentProvider 中数据库中的某个表，在这个例子中是 `User` 表。
- **1**: 这是具体记录的 **ID**，指向 `User` 表中 id 为 1 的某一行数据。如果没有具体的 ID，则表示操作整个表。

#### URI 中的通配符

- **`\*`**：表示匹配任意长度的任何有效字符。例如：

  ```
  less
  
  
  复制代码
  content://com.example.app.provider/*
  ```

  表示匹配该 Provider 中的任何内容。

- **`#`**：表示匹配任意长度的数字字符。例如：

  ```
  bash
  
  
  复制代码
  content://com.example.app.provider/table/#
  ```

  表示匹配该 Provider 中的 `table` 表的所有记录。

#### 使用示例

以下代码展示了如何解析和使用自定义 URI 来进行数据访问：

```
java复制代码// 创建一个 URI 对象
Uri uri = Uri.parse("content://com.carson.provider/User/1");

// 外部应用通过这个 URI 访问 "com.carson.provider" 中 "User" 表的 id 为 1 的数据
```

通过这种 URI 的定义和解析方式，应用可以通过 ContentProvider 实现跨进程的数据访问。





### MIME

MIME 类型用于指定 **某个 URI 对应的数据类型**。不同的 URI 会指向不同的数据记录或数据集合，而这些数据的类型需要通过 MIME 来描述，确保客户端应用可以正确理解并处理这些数据。

### 3. **ContentProvider 获取URI数据类型**

通过调用 `ContentProvider.getType(Uri uri)` 方法，客户端应用可以获取指定 URI 对应的数据类型（MIME）。ContentProvider 会根据 URI 的结构返回合适的 MIME 类型。

例如：

```
java


复制代码
String mimeType = getContentResolver().getType(uri);
```

### 4. **MIME 类型的组成**

每个 MIME 类型由两部分组成，格式为：

```
复制代码
类型/子类型
```

例如：

- `text/html`：类型是 `text`，子类型是 `html`，表示这是一个 HTML 文件。
- `application/pdf`：类型是 `application`，子类型是 `pdf`，表示这是一个 PDF 文件。

MIME返回值告知是单条还是多条

当 ContentProvider 返回数据时，通过 MIME 类型中的 `vnd.android.cursor.item/自定义` 和 `vnd.android.cursor.dir/自定义` 来告知客户端应用 **返回的是单条记录还是多条记录**。

举例

```
<-- 单条记录 -->
  // 单个记录的MIME类型
  vnd.android.cursor.item/vnd.yourcompanyname.contenttype 

  // 若一个Uri如下
  content://com.example.transportationprovider/trains/122   
  // 则ContentProvider会通过ContentProvider.geType(url)返回以下MIME类型
  vnd.android.cursor.item/vnd.example.rail


<-- 多条记录 -->
  // 多个记录的MIME类型
  vnd.android.cursor.dir/vnd.yourcompanyname.contenttype 
  // 若一个Uri如下
  content://com.example.transportationprovider/trains 
  // 则ContentProvider会通过ContentProvider.geType(url)返回以下MIME类型
  vnd.android.cursor.dir/vnd.example.rail
```



### ContentProvider

### 4.3.1 组织数据方式

**ContentProvider** 主要以**表格形式**组织和管理数据，类似于数据库表。每个表由 **行（记录）** 和 **列（字段）** 组成：

- **行**：代表数据库中的一条记录，例如某个用户的信息。
- **列**：代表记录中的一个字段，例如用户的名字或 ID。

除了表格数据外，ContentProvider 也可以用于文件存储和管理，例如图片或视频文件。不过，表格形式更为常见，因为很多应用使用 SQLite 数据库来组织数据，ContentProvider 通常作为应用内部数据库（如 SQLite）的接口，供其他应用访问。

### 4.3.2 主要方法

**ContentProvider** 的核心功能是提供**进程间的数据共享**，所以其核心操作与数据库基本一致，即 **增（insert）**、**删（delete）**、**改（update）** 和 **查（query）** 数据。这四个核心方法都是为了实现数据的基本操作需求。

以下是这四个核心方法的具体解释：

1. **`insert(Uri uri, ContentValues values)`**：
   - 该方法用于插入数据。外部进程通过 `insert()` 向 ContentProvider 添加数据。`ContentValues` 是键值对的形式，用来存储要插入的数据内容。
2. **`delete(Uri uri, String selection, String[] selectionArgs)`**：
   - 该方法用于删除数据。通过 `selection` 和 `selectionArgs` 来指定删除的条件。外部进程可以通过 URI 和条件指定删除的数据。
3. **`update(Uri uri, ContentValues values, String selection, String[] selectionArgs)`**：
   - 该方法用于更新数据。与 `delete()` 方法类似，外部进程通过指定条件和新的数据（通过 `ContentValues` 提供）来更新记录。
4. **`query(Uri uri, String[] projection, String selection, String[] selectionArgs, String sortOrder)`**：
   - 该方法用于查询数据。`projection` 用来指定需要查询的列，`selection` 和 `selectionArgs` 用来指定查询条件，`sortOrder` 用来指定结果的排序方式。返回值是一个 `Cursor` 对象，包含查询结果。

### 其他方法：

1. **`onCreate()`**：
   - 当 ContentProvider 创建时，或者当系统首次访问该 ContentProvider 时会调用该方法。此方法通常用于初始化数据存储或者数据库的连接。**注意：** `onCreate()` 是在主线程中执行的，不能进行耗时操作（例如初始化大型数据库或文件）。
2. **`getType(Uri uri)`**：
   - 该方法用于返回给定 URI 对应的数据的 **MIME 类型**。这对于确定数据格式非常重要，尤其在处理不同类型的内容（如图片、视频等）时，通过 MIME 类型可以确定合适的处理方式。

### 注意事项：

1. **线程安全**：
   - 由于这些方法运行在 ContentProvider 的进程中，并且会通过 Binder 线程池处理多线程并发请求，所以在设计 ContentProvider 时要注意线程安全问题。如果数据存储方式是 **SQLite**，通常不需要额外处理，因为 SQLite 内部已经实现了线程同步机制；但如果是使用其他方式（如内存或多个数据库实例），则需要手动实现线程同步，避免并发问题。
2. **跨进程通信**：
   - ContentProvider 是通过 Binder 机制进行进程间通信的。这意味着外部进程通过 `ContentResolver` 进行数据请求，而这些请求最终会通过 Binder 被传递到 ContentProvider 的进程，并在 ContentProvider 中的 Binder 线程池中执行。

### ContentProvider 与 ContentResolver 的关系：

- **ContentProvider** 并不直接与外部进程进行通信，外部应用不能直接操作 ContentProvider。
- 取而代之，Android 提供了 **ContentResolver** 类，**ContentResolver** 是外部进程访问 ContentProvider 的入口，它封装了对 ContentProvider 的调用，实现了跨进程通信。外部应用通过 ContentResolver 调用 ContentProvider 的方法来访问数据。







### 注意事项：

1. **线程安全**：
   - 由于这些方法运行在 ContentProvider 的进程中，并且会通过 Binder 线程池处理多线程并发请求，所以在设计 ContentProvider 时要注意线程安全问题。如果数据存储方式是 **SQLite**，通常不需要额外处理，因为 SQLite 内部已经实现了线程同步机制；但如果是使用其他方式（如内存或多个数据库实例），则需要手动实现线程同步，避免并发问题。
2. **跨进程通信**：
   - ContentProvider 是通过 Binder 机制进行进程间通信的。这意味着外部进程通过 `ContentResolver` 进行数据请求，而这些请求最终会通过 Binder 被传递到 ContentProvider 的进程，并在 ContentProvider 中的 Binder 线程池中执行。





理解：

**ContentProvider** 是对不同存储形式（如数据库或文件）的封装，使得数据访问不需要关心底层数据操作的具体实现细节。

ContentResolver是当前应用提供给外部应用的数据访问接口，是对ContentProvider 的封装。



###  ContentResolver 的作用

**ContentResolver** 的主要作用是统一管理**不同 ContentProvider 之间的操作**，简化了应用程序访问数据的流程。

简而言之，首先是简化了应用程序访问数据的流程。ContentProvider 的核心是通过 Binder 机制进行进程间通信，而 ContentResolver 隐藏了这种跨进程通信的复杂性。通过 ContentResolver，开发者可以像操作本地数据一样访问远程的数据，而不需要处理底层的跨进程通信细节。

统一管理**不同 ContentProvider 之间的操作**：一个应用可能会使用多个不同的 ContentProvider，每个 ContentProvider 可能有不同的实现方式和存储机制。如果直接与 ContentProvider 交互，开发者需要分别了解每个 ContentProvider 的具体实现，这样操作的复杂性会增加。使用 **URI**（统一资源标识符）可以让不同的 ContentProvider 暴露出统一的接口，开发者只需通过 URI 和 ContentResolver 就可以访问这些不同的数据源，而无需了解每个 ContentProvider 的内部实现。

### 4.4.3 具体使用

**ContentResolver** 提供了一系列与 **ContentProvider** 相同名称和功能的 CRUD 方法，允许开发者进行数据插入、删除、更新和查询操作。

- **insert()**：向指定 URI 对应的 ContentProvider 插入数据。
- **delete()**：根据 URI 删除指定的数据。
- **update()**：根据 URI 更新数据。
- **query()**：根据 URI 查询数据，并返回一个 `Cursor` 对象。

#### 使用示例：

1. **获取 ContentResolver**：

   - ContentResolver 是通过 `Context` 类获取的。所有继承自 `Context` 的类都可以通过 `getContentResolver()` 方法来获取 ContentResolver。

   ```
   java
   
   
   复制代码
   ContentResolver resolver = getContentResolver();
   ```

2. **设置 URI**：

   - URI 用于指定操作的 ContentProvider 和数据表。例如，`content://cn.scu.myprovider/user` 表示访问 `cn.scu.myprovider` 这个 ContentProvider 中的 `user` 表。

   ```
   java
   
   
   复制代码
   Uri uri = Uri.parse("content://cn.scu.myprovider/user");
   ```

3. **查询数据**：

   - 使用 `resolver.query()` 方法，基于 URI 查询数据。例如，查询 `user` 表中的所有记录，并按 `userid` 降序排列。

   ```
   java
   
   
   复制代码
   Cursor cursor = resolver.query(uri, null, null, null, "userid desc");
   ```

### 4.4.4 ContentProvider 辅助工具类

Android 提供了三个辅助工具类来简化 ContentProvider 的使用：

`Android` 提供了3个用于辅助`ContentProvide`的工具类：

- `ContentUris`
- `UriMatcher`
- `ContentObserver`



### 4.5 **ContentUris 类**

**作用**：用于操作 **URI**，特别是处理与 **ID** 相关的 URI 操作。

- 在 ContentProvider 中，通常需要通过 URI 来操作某一条特定的数据记录。ContentUris 类提供了简便的方法来构建或解析这种带有 ID 的 URI。

**核心方法**：

1. **`withAppendedId(Uri uri, long id)`**：

   - **作用**：向指定的 URI 后附加一个 ID，生成指向某条记录的 URI。

   - 示例

     ：

     ```
     java复制代码Uri uri = Uri.parse("content://cn.scu.myprovider/user");
     Uri resultUri = ContentUris.withAppendedId(uri, 7);  
     // 最终生成后的 URI 为：content://cn.scu.myprovider/user/7
     ```

   - 这种方法常用于创建指向特定记录的 URI，例如在查询或更新特定记录时。

2. **`parseId(Uri uri)`**：

   - **作用**：从一个 URI 中提取出 ID。

   - 示例

     ：

     ```
     java复制代码Uri uri = Uri.parse("content://cn.scu.myprovider/user/7");
     long personId = ContentUris.parseId(uri); 
     // 获取的结果为: 7
     ```

   - 这种方法常用于从 URI 中提取记录 ID，以便对具体的记录进行操作。

### 4.6 **UriMatcher 类**

**作用**：

- **UriMatcher** 用于在 **ContentProvider** 中注册和匹配 URI，不同的 URI 通常对应不同的数据表或资源。
- 它通过将 URI 与特定的 **URI_CODE** 进行匹配，使得 ContentProvider 能够根据 URI 的路径做出相应的处理。

**使用步骤**：

1. **初始化 UriMatcher 对象**：

   - 使用 `UriMatcher.NO_MATCH` 表示当前不匹配任何路径。

   ```
   java
   
   
   复制代码
   UriMatcher matcher = new UriMatcher(UriMatcher.NO_MATCH);
   ```

2. **注册 URI**：

   - 通过 `addURI()` 方法将 URI 与特定的 **URI_CODE** 绑定。在 `ContentProvider` 中，每个 URI 代表不同的数据表或资源。

   ```
   java复制代码matcher.addURI("cn.scu.myprovider", "user1", URI_CODE_a);
   matcher.addURI("cn.scu.myprovider", "user2", URI_CODE_b);
   ```

3. **匹配 URI**：

   - 使用 `match()` 方法来匹配 URI，并根据返回的 **URI_CODE** 来决定处理的逻辑。

   ```
   java复制代码@Override
   public String getType(Uri uri) {
       switch (matcher.match(uri)) {
           case URI_CODE_a:
               return "vnd.android.cursor.dir/vnd.cn.scu.myprovider.user1";
           case URI_CODE_b:
               return "vnd.android.cursor.dir/vnd.cn.scu.myprovider.user2";
           default:
               throw new IllegalArgumentException("Unknown URI: " + uri);
       }
   }
   ```

   - 通过 `matcher.match()` 方法，系统会根据 URI 返回对应的 **URI_CODE**，从而进行相应的数据库表或资源的操作。

### 4.7 **ContentObserver 类**

**作用**：

- **ContentObserver** 是一个监听器，它用于监听某个 **URI** 相关的 **ContentProvider** 数据的变化。当 **ContentProvider** 中的数据发生增删改时，会通过 **ContentObserver** 通知外部应用程序。
- 它通常用于实现实时更新机制，当数据变化时自动刷新 UI 或其他相关的应用逻辑。

**使用步骤**：

1. **注册 ContentObserver**：

   - 使用 `getContentResolver().registerContentObserver()` 方法注册一个内容观察者，并指定需要监听的 URI。

   ```
   java复制代码getContentResolver().registerContentObserver(uri, true, new ContentObserver(new Handler()) {
       @Override
       public void onChange(boolean selfChange) {
           // 数据发生变化时的处理逻辑
       }
   });
   ```

2. **通知数据变化**：

   - 当 **ContentProvider** 中的数据发生变化时，调用 `getContext().getContentResolver().notifyChange(uri, null)` 通知内容观察者。

   ```
   java复制代码public Uri insert(Uri uri, ContentValues values) {
       db.insert("user", "userid", values);
       getContext().getContentResolver().notifyChange(uri, null);
       return uri;
   }
   ```

3. **解除 ContentObserver**：

   - 当不再需要监听数据变化时，可以通过 `unregisterContentObserver()` 方法解除观察者。

   ```
   java
   
   
   复制代码
   getContentResolver().unregisterContentObserver(observer);
   ```

### 总结：

- **ContentUris**：用于简化带有 ID 的 URI 的构建和解析操作，特别是与数据记录的增删改查相关。
- **UriMatcher**：用于在 ContentProvider 中根据不同的 URI 匹配不同的资源或表，从而简化对不同 URI 的处理逻辑。
- **ContentObserver**：用于监听 ContentProvider 中的数据变化，当数据发生增删改时，通知外部应用并触发相应的操作。