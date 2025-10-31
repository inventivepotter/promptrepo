import { SimpleLocalStorage, createLocalStorage, globalLocalStorage, IStorage } from '../localStorage';

// Mock console.error
const originalConsoleError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
});

// A mock storage implementation for testing
const createMockStorage = (): IStorage & { store: Record<string, string> } => {
  const store: Record<string, string> = {};
  return {
    store,
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    getItem: jest.fn((key: string) => store[key] || null),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      Object.keys(store).forEach(key => delete store[key]);
    }),
  };
};

describe('SimpleLocalStorage', () => {
  let mockStorage: IStorage & { store: Record<string, string> };
  let localStorageInstance: SimpleLocalStorage;

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    // Create a fresh mock storage and localStorage instance for each test
    mockStorage = createMockStorage();
    localStorageInstance = new SimpleLocalStorage(mockStorage);
  });

  describe('with a mock storage implementation', () => {
    it('should set and get a string value', () => {
      const key = 'testStringKey';
      const value = 'hello world';
      localStorageInstance.set(key, value);
      expect(mockStorage.setItem).toHaveBeenCalledTimes(1);
      expect(mockStorage.setItem).toHaveBeenCalledWith(key, expect.any(String));
      const callArgs = (mockStorage.setItem as jest.Mock).mock.calls[0];
      const parsedValue = JSON.parse(callArgs[1]);
      expect(parsedValue.data).toBe(value);
      expect(typeof parsedValue.timestamp).toBe('number');
      const retrievedValue = localStorageInstance.get<string>(key);
      expect(retrievedValue).toBe(value);
      expect(mockStorage.getItem).toHaveBeenCalledWith(key);
    });

    it('should set and get a number value', () => {
      const key = 'testNumberKey';
      const value = 123;
      localStorageInstance.set(key, value);
      expect(mockStorage.setItem).toHaveBeenCalledTimes(1);
      expect(mockStorage.setItem).toHaveBeenCalledWith(key, expect.any(String));
      const callArgs = (mockStorage.setItem as jest.Mock).mock.calls[0];
      const parsedValue = JSON.parse(callArgs[1]);
      expect(parsedValue.data).toBe(value);
      expect(typeof parsedValue.timestamp).toBe('number');
      const retrievedValue = localStorageInstance.get<number>(key);
      expect(retrievedValue).toBe(value);
    });

    it('should set and get an object value', () => {
      const key = 'testObjectKey';
      const value = { name: 'Test', id: 1 };
      localStorageInstance.set(key, value);
      expect(mockStorage.setItem).toHaveBeenCalledTimes(1);
      expect(mockStorage.setItem).toHaveBeenCalledWith(key, expect.any(String));
      const callArgs = (mockStorage.setItem as jest.Mock).mock.calls[0];
      const parsedValue = JSON.parse(callArgs[1]);
      expect(parsedValue.data).toEqual(value);
      expect(typeof parsedValue.timestamp).toBe('number');
      const retrievedValue = localStorageInstance.get<object>(key);
      expect(retrievedValue).toEqual(value);
    });

    it('should set and get an array value', () => {
      const key = 'testArrayKey';
      const value = [1, 'two', { three: 3 }];
      localStorageInstance.set(key, value);
      expect(mockStorage.setItem).toHaveBeenCalledTimes(1);
      expect(mockStorage.setItem).toHaveBeenCalledWith(key, expect.any(String));
      const callArgs = (mockStorage.setItem as jest.Mock).mock.calls[0];
      const parsedValue = JSON.parse(callArgs[1]);
      expect(parsedValue.data).toEqual(value);
      expect(typeof parsedValue.timestamp).toBe('number');
      const retrievedValue = localStorageInstance.get<unknown[]>(key);
      expect(retrievedValue).toEqual(value);
    });

    it('should return null for a non-existent key', () => {
      const key = 'nonExistentKey';
      const retrievedValue = localStorageInstance.get<string>(key);
      expect(retrievedValue).toBeNull();
      expect(mockStorage.getItem).toHaveBeenCalledWith(key);
    });

    it('should clear a specific key', () => {
      const key = 'keyToClear';
      localStorageInstance.set(key, 'some data');
      expect(mockStorage.store[key]).toBeDefined();

      localStorageInstance.clear(key);
      expect(mockStorage.removeItem).toHaveBeenCalledWith(key);
      expect(mockStorage.store[key]).toBeUndefined();
    });

    it('should clear all keys', () => {
      localStorageInstance.set('key1', 'data1');
      localStorageInstance.set('key2', 'data2');
      expect(Object.keys(mockStorage.store).length).toBe(2);

      localStorageInstance.clearAll();
      expect(mockStorage.clear).toHaveBeenCalled();
      expect(Object.keys(mockStorage.store).length).toBe(0);
    });

    it('should handle JSON parsing errors gracefully and return null', () => {
      const key = 'malformedKey';
      (mockStorage.getItem as jest.Mock).mockReturnValueOnce('this is not valid json');
      const retrievedValue = localStorageInstance.get<string>(key);
      expect(retrievedValue).toBeNull();
      expect(console.error).toHaveBeenCalledWith(
        expect.stringContaining(`Failed to parse localStorage entry for key "${key}"`),
        expect.any(SyntaxError)
      );
    });

    it('should handle QuotaExceededError on set', () => {
      const key = 'quotaKey';
      const value = 'a very large string that would exceed quota';
      const error = new Error('QuotaExceededError');
      error.name = 'QuotaExceededError';
      (mockStorage.setItem as jest.Mock).mockImplementationOnce(() => {
        throw error;
      });

      localStorageInstance.set(key, value);
      expect(console.error).toHaveBeenCalledWith(
        expect.stringContaining(`Error setting item to localStorage for key "${key}"`),
        error
      );
    });
  });

  describe('createLocalStorage factory function', () => {
    let originalWindow: typeof window | undefined;

    afterEach(() => {
      // Restore window after each test in this describe block
      if (originalWindow) {
        global.window = originalWindow;
      } else {
        // @ts-expect-error: Simulating server-side by deleting window
        delete global.window;
      }
    });

    it('should use localStorage if window is defined', () => {
      // @ts-expect-error: Mocking window for test
      global.window = { localStorage: { setItem: jest.fn(), getItem: jest.fn(), removeItem: jest.fn(), clear: jest.fn() } };
      const instance = createLocalStorage();
      expect(instance).toBeInstanceOf(SimpleLocalStorage);
      // We can't easily check the internal storage implementation without reflection,
      // but the fact that it doesn't throw is a good sign.
    });

    it('should use a fallback in-memory store if window is not defined (server-side)', () => {
      originalWindow = global.window;
      delete (global as { window?: typeof window }).window;
      
      const instance = createLocalStorage();
      expect(instance).toBeInstanceOf(SimpleLocalStorage);

      const key = 'serverTestKey';
      const value = 'server side value';
      instance.set(key, value);
      const retrievedValue = instance.get<string>(key);
      expect(retrievedValue).toBe(value);
    });
  });

  describe('globalLocalStorage singleton', () => {
    it('should return the same instance on multiple calls', () => {
      const instance1 = globalLocalStorage();
      const instance2 = globalLocalStorage();
      expect(instance1).toBe(instance2);
    });

    it('should return a SimpleLocalStorage instance', () => {
      const instance = globalLocalStorage();
      expect(instance).toBeInstanceOf(SimpleLocalStorage);
    });

    it('should work with basic operations', () => {
      const instance = globalLocalStorage();
      const key = 'globalTestKey';
      const value = 'global test value';
      
      instance.set(key, value);
      const retrievedValue = instance.get<string>(key);
      expect(retrievedValue).toBe(value);
      
      instance.clear(key);
      const clearedValue = instance.get<string>(key);
      expect(clearedValue).toBeNull();
    });
  });
});