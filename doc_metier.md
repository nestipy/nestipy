# Documentation Métier de Nestipy

Nestipy est un framework Python inspiré par NestJS, conçu pour construire des applications côté serveur efficaces et évolutives. Ce document détaille le fonctionnement interne et la philosophie de conception du framework.

## 0. Modèles de Conception : Les Singletons

Nestipy utilise massivement le pattern Singleton, mais avec deux portées (scopes) distinctes :

### Singleton au niveau Application
La plupart des composants structurels sont des singletons persistants pendant toute la durée de vie du serveur :
- **`NestipyContainer`** : Gère l'injection de dépendances pour tous les services et contrôleurs.
- **`MiddlewareContainer`** : Stocke et gère les instances de middlewares.
- **Les Proxies (`RouterProxy`, `MicroserviceProxy`, etc.)** : Orchestrent la logique de routage.
- **Les Contrôleurs et Services** : Par défaut, ils sont instanciés une seule fois et partagés.

### Singleton au niveau Requête (Scope Request)
Certaines valeurs doivent être uniques pour chaque requête entrante. Bien qu'elles soient gérées via un conteneur "Singleton", leur état est éphémère :
- **`RequestContextContainer`** : Sert de point d'accès central pour les données de la requête en cours.
- **`Request` & `Response`** : Objets spécifiques à l'interaction HTTP actuelle.
- **`ExecutionContext`** : Fournit des métadonnées sur le handler en cours d'exécution.

> **Note importante** : Actuellement, le `RequestContextContainer` utilise une instance de classe unique réinitialisée à chaque requête. Une optimisation future via `ContextVar` est prévue pour garantir la sécurité dans les environnements asynchrones concurrents.

## 1. Comment fonctionnent les Adapteurs et comment créer le vôtre

L'architecture de Nestipy est agnostique vis-à-vis du framework Web sous-jacent grâce à l'utilisation d'une interface d'adaptation : `HttpAdapter`.

### Fonctionnement
Nestipy n'utilise pas directement des frameworks comme FastAPI ou BlackSheep. Au lieu de cela, il communique avec eux via un `HttpAdapter`. Cet adaptateur traduit les commandes Nestipy (définition de routes, gestion de middlewares) dans le langage spécifique du framework choisi.

### Créer son propre adaptateur
Pour créer votre propre adaptateur, vous devez hériter de la classe abstraite `HttpAdapter` (située dans `nestipy.core.adapter.http_adapter`) et implémenter toutes les méthodes abstraites :

```python
from nestipy.core.adapter.http_adapter import HttpAdapter

class MonNouvelAdapter(HttpAdapter):
    def get_instance(self) -> any:
        # Retourne l'instance du framework (ex: app FastAPI)
        pass

    def get(self, route: str, callback: Callable, metadata: dict = None):
        # Enregistre une route GET dans votre framework
        pass

    # Implémentez post, put, delete, ws, mount, etc.
```

## 2. Décorateurs et Injection de Dépendances (DI)

Nestipy utilise massivement les décorateurs et l'annotation de types pour gérer l'injection de dépendances.

### Injection par Propriété vs Méthode
- **Injection par Constructeur (Méthode)** : C'est la méthode recommandée. Les dépendances sont déclarées dans le constructeur `__init__`. Le `NestipyContainer` résout automatiquement ces dépendances lors de l'instanciation de la classe.
- **Injection par Propriété** : Vous pouvez annoter une propriété de classe avec `typing.Annotated[Type, Inject()]`. Nestipy parcourra les annotations de la classe et injectera les instances correspondantes.

### Fonctionnement interne
Le `NestipyContainer` est le coeur du système. Il maintient un registre des services (Singletons ou Transients). Lorsqu'une classe est demandée, le conteneur :
1. Examine les annotations du constructeur.
2. Résout récursivement chaque dépendance.
3. Instancie la classe.
4. Injecte les propriétés annotées.

## 3. Modules Dynamiques

Les modules dynamiques permettent de configurer un module lors de son importation (par exemple, passer des options de base de données).

### Comment ça marche
Un module dynamique est une méthode de classe (souvent `register` ou `for_root`) qui retourne un objet `DynamicModule`. Cet objet définit quels providers, contrôleurs ou imports doivent être ajoutés en fonction de la configuration passée.

### Création
Utilisez le `ConfigurableModuleBuilder` pour faciliter la création :
```python
from nestipy.dynamic_module import ConfigurableModuleBuilder

class MonModule:
    pass

ConfigurableBuilder, OPTIONS_TOKEN = ConfigurableModuleBuilder[MonOption]().build()

class MonModule(ConfigurableBuilder):
    @classmethod
    def register(cls, options: MonOption):
        return super().register(options)
```

## 4. Microservices

Nestipy supporte nativement les microservices via une couche d'abstraction de transport.

### Fonctionnement
Les contrôleurs utilisent des décorateurs comme `@MessagePattern` ou `@EventPattern`. Le `MicroserviceProxy` scanne ces contrôleurs et enregistre des "listeners" sur l'adaptateur de transport (Redis, NATS, etc.). Le flux de données est géré par un serveur de microservice qui reçoit les messages et les dispatche vers le bon handler Nestipy.

## 5. Injection et Vérification des Métadonnées

Les métadonnées sont essentielles pour le fonctionnement des décorateurs.

### Injection
Nestipy utilise une classe `Reflect` qui attache des données à un attribut spécial `__reflect__metadata__` sur les objets (classes, méthodes, fonctions). Le décorateur `@SetMetadata` est l'outil principal pour injecter ces données.

### Vérification
Lors de l'exploration des modules (par exemple par le `RouteExplorer`), Nestipy appelle `Reflect.get_metadata(obj, key)` pour lire les informations stockées (chemins des routes, méthodes HTTP, guards, etc.).

## 6. Proxies (Router, WebSocket, GraphQL)

Nestipy utilise des "Proxies" pour envelopper les gestionnaires de requêtes originaux.

- **Router Proxy** : Lorsqu'une route est enregistrée, elle n'est pas passée directement au framework Web. Elle est enveloppée dans un `request_handler`. Ce proxy gère :
    1. La création du contexte d'exécution.
    2. L'exécution des Middlewares.
    3. L'exécution des Guards (autorisation).
    4. L'exécution des Interceptors.
    5. Le rendu des templates ou la conversion de la réponse en JSON.
    6. La capture des exceptions.

- **WebSocket Proxy** : Similaire au routeur, il gère les connexions et les messages WebSocket, assurant que les guards et intercepteurs fonctionnent aussi sur les sockets.

- **GraphQL Proxy** : Intègre Strawberry ou d'autres librairies GraphQL dans le cycle de vie de Nestipy, permettant l'utilisation de l'injection de dépendances et des guards dans les résolveurs GraphQL.

## 7. Reverse Engineering du Framework

Voici le cycle de vie complet d'une exécution dans Nestipy, de l'initialisation à la réponse.

### Phase 1 : Initialisation de l'Application
1.  **Démarrage** : `NestipyFactory` crée l'instance de l'application.
2.  **Conteneurisation** : Le `NestipyContainer` est initialisé. Il scanne le module racine (`AppModule`) et ses dépendances.
3.  **Exploration** : Les explorateurs (`RouteExplorer`, `GraphqlExplorer`) scannent les contrôleurs pour en extraire les routes, guards, intercepteurs et métadonnées via `Reflect`.
4.  **Adaptation** : Le framework enregistre les handlers dans l'adaptateur sélectionné (FastAPI ou BlackSheep). Chaque route est enveloppée par le `RouterProxy`.

### Phase 2 : Cycle de Vie d'une Requête (Request Lifecycle)
Lorsqu'une requête HTTP arrive :
1.  **Création du Contexte** : Le `RouterProxy` crée un `ExecutionContext` contenant la requête, la réponse, et les métadonnées du contrôleur.
2.  **Scope Request** : Le `RequestContextContainer` est mis à jour avec cet `ExecutionContext`. Cela permet l'injection de `Req`, `Res`, ou `Context` n'importe où dans le code.
3.  **Exécution des Middlewares** : Le `MiddlewareExecutor` parcourt la liste des middlewares correspondants à l'URL.
4.  **Garde (Guards)** : Les "Guards" sont exécutés pour vérifier les autorisations.
5.  **Intercepteurs (Pré-traitement)** : Les intercepteurs peuvent manipuler les données avant qu'elles n'atteignent le contrôleur.
6.  **Appel du Handler** : Le contrôleur est résolu par le `NestipyContainer`, ses dépendances sont injectées, et la méthode cible est appelée.
7.  **Intercepteurs (Post-traitement)** : Les intercepteurs manipulent la réponse du contrôleur.
8.  **Rendu & Réponse** : Le framework transforme le résultat (dict, str, dataclass) en une réponse HTTP finale via `_ensure_response`.
9.  **Nettoyage** : `RequestContextContainer.destroy()` est appelé pour libérer le contexte de la requête.
