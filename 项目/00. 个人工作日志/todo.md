[toc]

## 01.Retrofit动态代理

```
interface UpdateService {
    @GET("api/version")
    suspend fun getGeneralVersion(@Query("type") type: String): Response<VersionInfo>
}

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .build()

val updateService = retrofit.create(UpdateService::class.java)
```

- 这行代码的作用是：让 Retrofit 动态生成一个实现了 UpdateService 接口的对象。

- 这个对象不是你自己写的实现类，而是 Retrofit 用动态代理（Java Proxy）在运行时生成的。



### 动态代理的原理

- 当你调用 updateService.getGeneralVersion(...) 时，实际上是调用了代理对象的 invoke() 方法。

- 代理对象会：

1. 解析你接口方法上的注解（如 @GET、@POST、@Query 等）

1. 组装 HTTP 请求（URL、参数、请求体等）

1. 用 OkHttp 发起网络请求

1. 把响应结果解析成你定义的返回类型（如 Response<VersionInfo>）

------

### 4. 这样做的好处

- 你只需要声明接口和注解，不用写任何网络请求的实现代码。

- Retrofit 自动帮你完成所有底层细节，让网络请求像调用本地方法一样简单。

------

### 5. 底层源码简要说明

- retrofit.create() 内部会用 Java 的 Proxy.newProxyInstance() 创建代理对象。

- 代理对象的 invoke() 方法会根据方法注解和参数，动态组装请求并执行。