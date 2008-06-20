
/**
 * <p>When a command is received from the IRC Server, it is parsed
 * by the Command object. The Command object then selects the appropriate
 * CommandProcessingStrategy with which to process the command.
 *
 * <p>Only one of each CommandProcessingStrategy will be instantiated,
 * so you should not store any state in the object that you wouldn't want
 * shared between repeated invocations of the execute() method. On the other
 * hand, the execute() method is only ever processed by one thread at a time
 * so it does not have to be reentrant.
 *
 * <p>Normally, you'd have one Strategy per command word, but since we are
 * optimizing for download size, it's probably necessary to sacrifice
 * that granularity and have a Strategy for each family of commands.
 *
 * <p>Uses the Strategy Pattern (Gamma et al, p315)
 *
 * @version $Id: CommandProcessingStrategy.java,v 1.2 2003/12/02 22:08:19 bryan_w Exp $
 */
public interface CommandProcessingStrategy {
    /**
     * Performs the work of command processing. It does not have to be reentrant,
     * the framework guarantees that only one thread will enter this method
     * at a time.
     */
    void execute(Command command, Chat session);

    /**
     * <p>Register a Strategy with the Command object.
     * Strategies are responsible for telling the Command object
     * what commands they are interested in, using its registerStrategy()
     * method.
     */
    void register();
}
