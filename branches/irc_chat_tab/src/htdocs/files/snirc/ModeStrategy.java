

/**
 * <p>Handles the numerics for MODE replies from the server.
 * Currently we ignore everything but hannel modes for the
 * currently active channel.
 *
 * @version $Id: ModeStrategy.java,v 1.2 2003/12/02 22:08:19 bryan_w Exp $
 */
public class ModeStrategy implements CommandProcessingStrategy {
    /**
     * Performs the work of command processing. It does not have to be reentrant,
     * the framework guarantees that only one thread will enter this method
     * at a time.
     */
    public void execute(Command command, Chat session) {
        if (!session.isCurrentChannel(command.getArgument(0)))
            return;

        boolean settingMode = false;
        String modeBlock = command.getArgument(1);
        int currArg = 2;
        for (int i = 0; i < modeBlock.length(); i++) {
            switch (modeBlock.charAt(i)) {
                case '+':
                    settingMode = true;
                    break;
                case '-':
                    settingMode = false;
                    break;
                case 'o':
                    session.changeNickMode(command.getArgument(currArg++), 'o', settingMode);
                    break;
                case 'v':
                    session.changeNickMode(command.getArgument(currArg++), 'v', settingMode);
                    break;
                case 'b': // fall through
                case 'l': // fall through
                case 'k': // fall through
                    currArg++;
            } // end switch
        } // end for
        session.sendToUser(
                "[M] "
                + command.getSource()
                + " has set mode(s) "
                + command.getArguments(1)
                + " on channel "
                + command.getArgument(0));
    }

    /**
     * <p>Register a Strategy with the Command object.
     * Strategies are responsible for telling the Command object
     * what commands they are interested in, using its registerStrategy()
     * method.
     */
    public void register() {
        Command.registerStrategy("MODE", this);
    }
}
